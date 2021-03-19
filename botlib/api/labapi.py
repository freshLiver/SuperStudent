import struct
import socket
from json import loads
from pathlib import Path

# project libs
from botlib.botlogger import BotLogger
from botlib import BotConfig


class LabApi :
    
    @staticmethod
    def __format_data( token: str, raw_data: str ) -> bytes :
        """
        convert raw data to wmmks lab's api format
        
        :param token: user api token
        :param raw_data: data will be send to server
        :return: formatted data
        """
        
        # concatenate user token and data with @@@, and convert to bytes
        formatted_data = bytes(token + "@@@" + raw_data, "utf-8")
        
        # convert msg msg length(unsigned int) to bytes, and put before msg
        formatted_data = struct.pack(">I", len(formatted_data)) + formatted_data
        
        return formatted_data
    
    
    @staticmethod
    def __base_sender( token: str, raw_data: str, host_port: tuple ) -> bytes or None :
        """
        WMMKS lab's api handler,
        this method will convert raw data into lab data's format,
        and then send to server and get response in bytes (or None while something wrong)
        
        :param token: user token of target WMMKS lab's api
        :param raw_data: data will be send to server
        :param host_port: api's host ip and port
        :return: byte data or None
        """
        
        # response data
        response = None
        
        # init tcp socket fd
        api = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
        
        try :
            # connect server with this socket
            api.connect(host_port)
            BotLogger.log_debug("Connecting To Lab API Done")
            
            # send data to server
            api.sendall(LabApi.__format_data(token = token, raw_data = raw_data))
            BotLogger.log_debug("Sending Data To Lab API Done.")
            
            # recv from server and return data
            response = api.recv(8096)
            BotLogger.log_debug("Receiving Data From Lab API Done.")
        
        
        except ConnectionError as e :
            BotLogger.log_exception(f"Lab API Connection Error : {e}")
        
        except Exception as e :
            BotLogger.log_exception(f"Exception ({type(e).__name__}) : {e}")
        
        finally :
            api.close()
            BotLogger.log_debug("Lab API Socket Had Been Closed.")
        
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
        token = BotConfig.get_lab_ner_token()
        
        # send content to server and recv ner result
        result = LabApi.__base_sender(token, cht_text, BotConfig.get_lab_ner_host_port())
        
        # decode as utf-8 and convert to dict
        if result is not None :
            result = loads(str(result, "utf-8"))
            BotLogger.log_info("Getting NER Result From Lab API Done.")
        
        # return result dict
        return result
    
    
    @staticmethod
    def lab_c2t_api( userid: str, cht_text: str ) -> Path or None :
        """
        WMMKS Lab's CHT Text to Taiwanese Speech System API,
        this method will convert cht text into taiwanese speech
        and then save as audio_output_dir/userid.wav
        
        :param userid: line user id, which will be then filename of tmp speech output file
        :param cht_text: cht text which will be convert to taiwanese speech
        :return: taiwanese speech audio file's abs path (None if something wrong)
        """
        
        # get api token
        token = BotConfig.get_lab_ner_token()
        
        # send text to server and get result
        speech_data = LabApi.__base_sender(token, cht_text, BotConfig.get_lab_c2t_host_port())
        
        # if result not None, output bytes to file.wav
        if speech_data is not None :
            try :
                # determine speech output dir
                output = BotConfig.file_path_from(BotConfig.get_audio_output_dir(), userid, ".wav")
                
                # output api response bytes to target file
                with open(output, "wb") as file :
                    file.write(speech_data)
                
                # return speech audio abs path
                return output
            
            except Exception as e :
                BotLogger.log_exception(f"Exception {type(e).__name__} : {e}")
        
        return None


if __name__ == '__main__' :
    res = LabApi.lab_ner_api("今天成功大學有活動")
    print(res)