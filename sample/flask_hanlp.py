import json
import hanlp

# flask libs
from flask import Flask, request, jsonify

# proj libs
from botlib import BotConfig



HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
app = Flask(__name__)


@app.route("/NLP", methods = ["POST"])
def build_dict() :
    try :
        # get json content from post request
        try :
            post_data = json.loads(request.get_json())
        except TypeError :
            # curl POST will be here
            post_data = request.get_json()

        # try to extract useful data from dict
        sentence_list = post_data["sentences"]
        if type(sentence_list) is not list :
            raise TypeError

        custom_dict = post_data["custom_dict"]
        if type(custom_dict) is not dict :
            raise TypeError

        # set custom dict (low priority, combine tokens after ws)
        HanLP['tok/fine'].dict_combine = custom_dict

        # tokenize sentences base on custom_dict
        ws_result = HanLP(sentence_list)['tok/fine']

        # do pos and ner base on tokens
        pn_result = HanLP(ws_result, tasks = ['pos', 'ner'], skip_tasks = 'tok*')

        # return ws, pos, ner result as json(dict)
        result = {
            "WS" : ws_result,
            "POS" : pn_result['pos/ctb'],
            "NER" : pn_result['ner/msra']
        }

        return jsonify(result)

    except TypeError :
        error_msg = { "Type Error" : "Wrong Value of Key, Value Should Be : \"sentences\":list, \"custom_dict\":dict " }
        return jsonify(error_msg)

    except KeyError :
        error_msg = { "Key Error" : "POST Dict Should Contain 2 Keys : \"sentences\" and \"custom_dict\"" }
        return jsonify(error_msg)


@app.route("/", methods = ["GET"])
def home() :
    return "Home Page Of BotNLP."


if __name__ == '__main__' :
    app.run(debug = True, port = BotConfig.PORT)