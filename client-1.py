from openai import OpenAI
# load the large language model file
#from llama_cpp import Llama

from flask import Flask, request, jsonify
from flask_cors import CORS

import time
import requests

app = Flask(__name__)
CORS(app)

client = OpenAI( api_key="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")
client1 = OpenAI( api_key="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")
#LLM = Llama(model_path="../llamacpp//llama-2-7b-chat.Q4_0.gguf")


def handle_openai(request):
    data = request.get_json(True)  # Get the JSON data from the request
    storyDescription = data.get("message", "No message provided")

    print("Received ", storyDescription)
    
    # storyDescription = "Users should be able to search and find the books"

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role":"system", "content":"You are an agile coach who strictly reviews the JIRA stories to complaint with INVEST principles. Also good rewriting the user story inline with INVEST, provide acceptance criteria, BDD Test cases and synthetic test data. only output user story."}, 
                { "role": "user", "content": "Rewrite the following user story to align it with INVEST principles along with clear acceptance criteria, BDD Test cases and synthetic test data. This will be used as it is in JIRA story board. So provide them as user story, Acceptance Criteria, Test cases.\n " + "\nStory:\n" + storyDescription}]
    )
    content = chat_completion.choices[0].message.content


    # You can process the message here and return a response
    response = {
        
        "original_story": storyDescription,
        "refined_story": content
    }

    print(content, "Done processing")
    return jsonify(response), 200

def handle_openai_vision(request):
    data = request.get_json(True)  # Get the JSON data from the request
    storyDescriptions = data.get("message", "No message provided")

    print("Received ", storyDescriptions)
    
    headers = {
       "Content-Type": "application/json",
       "Authorization": f"Bearer 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"
    }

    messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "I am developing a feature called security center. out of these two screenshots, from the first screen, when view more is clicked, it goes to second screen. Identify various UI components related to this flow.in the second screen, they are not check boxes. they are mobile or tablet or desktop icon.. indicates which device was used to login. create jira user stories for last sign in portion in the first screen and the whole second screen. Ensure it follows INVEST principles and includes acceptance criteria, bdd testcases"
            },
        ] + [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{storyDescription}"
                }
            } for storyDescription in storyDescriptions
        ]
    }
]

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": messages,
    "max_tokens": 1000
}  
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
   
    content = response.json().get("choices")[0].get("message").get("content")
    print(content, "Done processing")
    responseObj = {
        
        
        "refined_story": content
    }
    #print(response.json())
    #print("Done:", newResponse)
    return jsonify(responseObj), 200


   

@app.route('/refine', methods=['POST'])
def process_refine():
    print(request.data)
 
    if request.is_json:
        data = request.get_json(True)  # Get the JSON data from the request
        provider = data.get("provider", "GPT")
        print("in refine",provider)

        if provider  == "GPT":
            print("in refine---openai", data)
            return handle_openai(request)
        else:
          print("in else")
          return handle_openai_vision(request)
            
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    


def detect_openai(request):
    data = request.get_json(True)  # Get the JSON data from the request
    storyDescription = data.get("message", "No message provided")

    print("Received ", storyDescription)
    
    # storyDescription = "Users should be able to search and find the books"

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role":"system", "content":"""You are an agile coach. Perform following validations on the user story provided and output the failed validations ONLY. Do not show passed validations. 
                1: The story points should be maximum 5. \n\n
                2: The story should have a feature ID\n\n
                3: Acceptance Criteria is written in GWT (Given, When, Then) format and should cover all (one or more) scenarios\n\n
                4: The story has a Project Id and Application name associated with it\n\n
                5: All (one or more) dependencies are called out as a part of the user story using linked issues option\n\n
                6: Story should have a NO for blocker or dependency\n\n
                7: The story has fix-version\n\n
                8: The story has at least one attachment related to prototypes or wireframes or copy deck"""}, 
                { "role": "user", "content": "USER STORY DETAILS: \n\n " + storyDescription}]
    )
    content = chat_completion.choices[0].message.content
 
    # You can process the message here and return a response
    response = {
        
        # "original_story": storyDescription,
        "findings": content
    }

    print(content, "Done processing")
    return jsonify(response), 200


@app.route('/detect', methods=['POST'])
def process_detect():
    print(request.data)
 
    if request.is_json:
        data = request.get_json(True)  # Get the JSON data from the request
        provider = data.get("provider", "openai")

        if provider  == "openai":
            return detect_openai(request)
        
            
    else:
        return jsonify({"error": "Request must be JSON"}), 400
 

if __name__ == '__main__':

    app.run(debug=True)

