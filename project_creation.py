import requests

url = "http://localhost:8080/api/projects"
headers = {
    "Authorization": "Token 107ed1f5cc82a5837866eab5b6f998999f5626ef",
    "Content-Type": "application/json"
}
payload = {
    "title": "Postman Project",
    "description": "project creation",
    "label_config": """
    <View>
        <Image name="image" value="$image"/>
        <RectangleLabels name="label" toName="image">
            <Label value="postmanlabel1" background="green"/>
            <Label value="postmanlabel2" background="blue"/>
        </RectangleLabels>
    </View>
    """
}

response = requests.post(url, headers=headers, json=payload)

print(response.status_code)
print(response.json())
