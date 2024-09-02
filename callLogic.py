import requests
import json

def call_logic_app(to, subject, body):
    # Replace with your Logic App HTTP POST URL
    return {'entering logic app'}
    logic_app_url = "https://prod-25.northcentralus.logic.azure.com:443/workflows/b1783a48359041a6b81ffc4f1496ae1b/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=6OFaWBJZWczrYsHFPJnYwN2tu2wLwB_Awu-1YAE-I1I"

    # Prepare the payload
    payload = {
        "to": to,
        "subject": subject,
        "body": body
    }

    # Send the POST request
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(logic_app_url, headers=headers, data=json.dumps(payload))

    # Check the response
    if (response.status_code == 200 or response.status_code == 202):
        return{'Email sent successfully!'}
        return
    else:
        reutnr{'Failed to send email. Status code: {response.status_code}, Response: {response.text}'}
        return
    
if __name__ == '__main__':
    def callLogic(to, subject, body):
        pass
