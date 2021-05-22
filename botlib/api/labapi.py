import struct
import socket
from json import loads
from pathlib import Path

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger
from botlib.converter.audio_converter import AudioConvert



class LabApi :

    @staticmethod
    def __format_text_data( token: str, raw_text: str ) -> bytes :

        # concatenate user token and data with @@@, and convert to bytes
        data = bytes(token + "@@@" + raw_text, "utf-8")

        # convert msg msg length(unsigned int) to bytes, and put before msg
        data = struct.pack(">I", len(data)) + data

        return data


    @staticmethod
    def __format_audio_data( token: str, audio_path: Path ) -> bytes :

        audio_data = open(audio_path, "rb").read()
        data = bytes(token + "@@@", "utf-8") + struct.pack("8s", bytes("main", encoding = "utf8")) + b"P" + audio_data
        data = struct.pack(">I", len(data)) + data

        return data


    @staticmethod
    def __base_sender( data: bytes, host_port: tuple ) -> bytes or None :

        # response data
        response = None

        # init tcp socket fd
        api = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)

        try :
            # connect server with this socket
            api.connect(host_port)
            BotLogger.debug("Connecting To Lab API Done")

            # send data to server
            api.sendall(data)
            BotLogger.debug("Sending Data To Lab API Done.")

            # recv ALL byte from server and return data
            response = bytes()
            while True :
                buffer = api.recv(1024)
                if buffer == bytes() :
                    break
                else :
                    response += buffer

            BotLogger.debug("Receiving Data From Lab API Done.")


        except ConnectionError as e :
            BotLogger.exception(f"Lab API Connection Error : {e}")

        except Exception as e :
            BotLogger.exception(f"Exception ({type(e).__name__}) : {e}")

        finally :
            api.close()
            BotLogger.debug("Lab API Socket Had Been Closed.")

        # return response or None (Error)
        return response


    @staticmethod
    def lab_ner_api( cht_text: str ) -> dict or None :
        """
        WMMKS Lab's NER System API,
        this method will send cht text to server
        and then get NER result as dict
        
        :param cht_text: cht text to do NER analyze
        :return: NER result dict (None if something wrong)
        """

        # get ner token
        token = BotConfig.LAB_NER_TOKEN

        # send content to server and recv ner result
        data = LabApi.__format_text_data(token, cht_text)
        result = LabApi.__base_sender(data, BotConfig.LAB_NER_HOST_PORT)

        # decode as utf-8 and convert to dict
        if result is not None :
            result = loads(str(result, "utf-8"))
            BotLogger.debug("Getting NER Result From Lab API Done.")

        # return result dict
        return result


    @staticmethod
    def lab_c2t_api( output_filename: str, cht_text: str ) -> Path or None :
        """
        WMMKS Lab's CHT Text to Taiwanese Speech System API,
        this method will convert cht text into taiwanese speech
        and then save as audio_output_dir/userid.wav
        
        :param output_filename: line user id, which will be then filename of tmp speech output file
        :param cht_text: cht text which will be convert to taiwanese speech
        :return: taiwanese speech audio file's abs path (None if something wrong)
        """

        # get api token
        token = BotConfig.LAB_C2T_TOKEN

        # send text to server and get result
        data = LabApi.__format_text_data(token, cht_text)
        speech_data = LabApi.__base_sender(data, BotConfig.LAB_C2T_HOST_PORT)

        # if result not None, output bytes to file.wav
        if speech_data is not None :
            try :
                # determine speech output dir
                output = BotConfig.file_path_from(BotConfig.AUDIO_OUTPUT_TMP_DIR, output_filename, ".wav")

                # output api response bytes to target file
                with open(output, "wb") as file :
                    file.write(speech_data)

                # return speech audio abs path
                return output

            except Exception as e :
                BotLogger.exception(f"Exception {type(e).__name__} : {e}")

        return None


    @staticmethod
    def lab_t2c_api( taiwanese_text: str ) -> str :

        token = BotConfig.LAB_T2C_TOKEN

        data = LabApi.__format_text_data(token, taiwanese_text)
        result = LabApi.__base_sender(data, BotConfig.LAB_T2C_HOST_PORT)

        return result.decode("utf-8")


    @staticmethod
    def lab_tstt_api( wav_16khz_audio_path: Path ) -> str :


        data = LabApi.__format_audio_data(BotConfig.LAB_TSTT_TOKEN, wav_16khz_audio_path)
        bytes_result = LabApi.__base_sender(data, BotConfig.LAB_TSTT_HOST_PORT)

        result = bytes_result.decode("utf-8")
        # get best match
        try :
            return result.split("1.")[1].split(" ")[0]
        except :
            return ""


if __name__ == '__main__' :
    from pprint import pprint



    wav_path = LabApi.lab_c2t_api("test_tai", "我今天肚子不舒服")
    out_path = Path(wav_path.__str__() + "_16k.wav")
    AudioConvert.ffmpeg_convert(wav_path, out_path, 2, 16000)
    path = Path(out_path)
    ttext = LabApi.lab_tstt_api(path)
    res = LabApi.lab_t2c_api("")

    pprint(res)