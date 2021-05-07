import os
import json
import hanlp

from flask import abort, Flask, jsonify, request



app = Flask(__name__)
HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)


@app.route('/')
def index() :
    return 'Flask-HanLP API is running!'


@app.route("/HANLP", methods = ["POST"])
def nlp() :
    # TODO : ADD LOG FOR THIS
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


if __name__ == '__main__' :
    # certificate and key files
    context = ('server.crt', 'server.key')
    app.run(host = '0.0.0.0', port = 7778, debug = True, ssl_context = context)