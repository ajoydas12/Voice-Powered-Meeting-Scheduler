# **Voice-Powered Meeting Scheduler**

A conversational voice assistant that schedules Google Calendar meetings and sends email notifications based on your voice commands.  
This project uses a local Python script as the voice client and an n8n workflow powered by the Gemini API for backend automation.

## **Overview**

This project provides a hands-free way to schedule meetings.  
You start the Python script, state your full request (e.g., "schedule a meeting with jane@example.com tomorrow from 2 to 3 PM"), and the assistant sends this command to an n8n workflow. The workflow uses the Gemini API to understand the command, creates the Google Calendar event, and sends a confirmation email.

## **Features**

* **Natural Language Processing** – Uses the Gemini API to understand complex, single-sentence commands.  
* **Voice-Controlled** – Fully hands-free operation.  
* **Backend Automation** – Uses **n8n** to integrate the Gemini API, Google Calendar, and email services.  
* **Robust Error Handling** – Handles common speech recognition and network issues.  
* **Configurable** – Centralized settings for prompts and keywords.

## **Architecture**

The system is divided into two main components:

### **1\. Python Voice Client (main.py)**

* Runs on your **local machine**.  
* Uses SpeechRecognition for voice-to-text and pyttsx3 for text-to-speech.  
* Captures the user's full voice command as a single sentence.  
* Sends this sentence as a **JSON payload** to the **n8n webhook**.

### **2\. n8n Workflow**

* Listens for requests from the Python client via a **Webhook node**.  
* Uses a **Gemini API node** to parse the sentence and extract meeting details into a structured JSON format.  
* Uses a **Google Calendar node** to create the meeting using the data from the Gemini node.  
* Uses a **Send Email / Gmail node** to send confirmation emails.  
* Sends a final **confirmation response** back to the Python client.

## **Prerequisites**

Before starting, make sure you have:

* **Python 3.8+**  
* **n8n**: Installed locally or via Docker  
  npm install n8n \-g

* **Google Cloud Account**:  
  * Enable the **Google Calendar API**  
  * Enable the **Vertex AI API** (for Gemini)  
  * Create mainropriate API Keys or Service Account credentials.  
* **Email Account** (e.g., Gmail) for sending confirmations.

## **Setup Instructions**

### **1\. n8n Workflow Setup**

1. **Start n8n**:  
   n8n start

2. #### **Create a New Workflow with the following nodes:**    **Node 1: Webhook**

   * Trigger for incoming requests.  
   * Receives a JSON object like: {"command": "Schedule a meeting with..."}

   **Node 2: Gemini API**

   * #### **Authenticate with your Google Cloud / Vertex AI credentials.**

   * **Prompt:**  
        You are an expert assistant that extracts meeting details from text. Given the text below, extract the date, start time, end time, and a suitable subject for the meeting.

        **Instructions:**
        1. give subject is "Meeting with HR".
        2. The current date is ```{{ new Date().toISOString() }}```. If the user mentions a date that has already passed this year (e.g., says "January 5th" when it's August), assume they mean for the next year.

        **Output Format:**
        Respond ONLY with a valid JSON object containing these exact keys: "email", "date" (in YYYY-MM-DD format), "startTime" (in HH:mm 24-hour format), "endTime" (in HH:mm 24-hour format), and "subject" (as a string).

        **Text:**
        ```{{$json.body}}```

   **Node 3: Google Calendar**

   * #### **Operation: Create**

   * **Authenticate** with your Google account.  
   * **Fields** (Note: these expressions parse the JSON *string* returned by the Gemini node):  
     * **Title:** ```{{ JSON.parse($json.content.parts[0].text).subject }} ``` 
     * **Start Time:** ```{{ JSON.parse($json.content.parts[0].text).date }} {{ JSON.parse($json.content.parts[0].text).startTime }} ``` 
     * **End Time:** ```{{ JSON.parse($json.content.parts[0].text).date }} {{ JSON.parse($json.content.parts[0].text).endTime }} ``` 
     * **Attendees:** ```{{ JSON.parse($json.content.parts[0].text).email }}```

   **Node 4: Send Email**

   * #### **Authenticate with your email provider.**

   * **To:** ```{{ $json.attendees[0].email }}  ```
   * **Subject:** ```{{ $json.summary }} ``` 
   * **HTML Body:** Use a confirmation email template.

   **Node 5: Respond to Webhook**

   * #### **Response Body:**   ```   **{**        **"message": "All done\! I have scheduled the meeting and sent the confirmation email."**      **}** ```

3. **Connect the Nodes**:  
   Webhook → Gemini API → Google Calendar → Send Email → Respond to Webhook

4. **Save & Activate** the workflow and copy the **Production URL**.

### **2\. Python Client Setup**

1. **Save the script** as main.py.  
2. **Create a requirements.txt file** in the same directory as main.py and add the following content:  
   SpeechRecognition  
   PyAudio  
   pyttsx3  
   requests

3. **Create & Activate a Virtual Environment**:  
   python \-m venv venv

   **Activate it:**  
   * macOS/Linux: source venv/bin/activate  
   * Windows: .\\venv\\Scripts\\activate  
4. **Install Dependencies**:  
   pip install \-r requirements.txt  
   **Note:** If PyAudio fails on Debian/Ubuntu, run: sudo apt-get install portaudio19-dev python-pyaudio  
5. **Configure the Script**:  
   * Open main.py.  
   * Paste the **Production URL** from your n8n Webhook into the N8N\_WEBHOOK\_URL variable.

## **Usage**

1. **Start the n8n workflow**.  
2. **Run the Python script**:  
   python main.py

3. The assistant will greet you.  
4. State your full command in one sentence, for example:"Schedule a meeting with ajoy.das@example.com tomorrow from 4 PM to 5 PM about the project review."  
5. The assistant will send the command to n8n, which will use Gemini to process it, schedule the meeting, and send the confirmation.  
6. To **stop the assistant**, say "stop" or "goodbye".