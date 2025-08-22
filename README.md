````markdown
# Voice-Powered Meeting Scheduler

A conversational **voice assistant** that schedules Google Calendar meetings and sends email notifications based on your **voice commands**.  
This project uses a **local Python script** as the voice client and an **n8n workflow** for backend automation.

---

## **Overview**

This project provides a **hands-free way** to schedule meetings.  
You start the Python script, say **"schedule a meeting"**, and the assistant will conversationally ask for:

- Guest's email
- Date of the meeting
- Start and end times

After confirming each detail, it sends the information to an **n8n workflow**, which automates:

- Creating the **Google Calendar** event
- Sending a **confirmation email** to the attendee

---

## **Features**

- **Conversational Interface** – The assistant guides you step by step.
- **Voice-Controlled** – Fully hands-free operation.
- **Email Validation** – Ensures correct email formatting.
- **Backend Automation** – Uses **n8n** to integrate Google Calendar and email services.
- **Robust Error Handling** – Handles common speech recognition and network issues.
- **Configurable** – Centralized settings for prompts, keywords, and confirmations.

---

## **Architecture**

The system is divided into two main components:

### **1. Python Voice Client (`main.py`)**

- Runs on your **local machine**.
- Uses:
  - [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/) for voice-to-text.
  - [`pyttsx3`](https://pypi.org/project/pyttsx3/) for text-to-speech responses.
- Manages conversational flow to collect meeting details.
- Sends structured meeting data as a **JSON payload** to the **n8n webhook**.

### **2. n8n Workflow**

- Listens for requests from the Python client via a **Webhook node**.
- Uses:
  - **Google Calendar node** → Creates the meeting.
  - **Send Email / Gmail node** → Sends confirmation emails.
- Sends a final **confirmation response** back to the Python client.

---

## **Prerequisites**

Before starting, make sure you have:

- **Python 3.8+**
- **n8n**: Installed locally or via Docker  
  ```bash
  npm install n8n -g
````

* **Google Cloud Account**:

  * Enable the **Google Calendar API**
  * Create **OAuth 2.0 credentials**
* **Email Account** (e.g., Gmail) for sending confirmations.

---

## **Setup Instructions**

### **1. n8n Workflow Setup**

1. **Start n8n**:

   ```bash
   n8n start
   ```

2. **Create a New Workflow** with the following nodes:

   #### **Node 1: Webhook**

   * Trigger for incoming requests.
   * Copy the **Test URL** for now.

   #### **Node 2: Google Calendar**

   * **Operation:** `Create`
   * **Authenticate** with your Google account.
   * **Fields**:

     * **Title:** `{{ JSON.parse($json.content.parts[0].text).subject }}`
     * **Start Time:**

       ```js
       {{ JSON.parse($json.content.parts[0].text).date }} {{ JSON.parse($json.content.parts[0].text).startTime }}
       ```
     * **End Time:**

       ```js
       {{ JSON.parse($json.content.parts[0].text).date }} {{ JSON.parse($json.content.parts[0].text).endTime }}
       ```
     * **Attendees:** `{{ JSON.parse($json.content.parts[0].text).email }}`

   #### **Node 3: Send Email**

   * Authenticate with your email provider.
   * **To:** `{{ $json.attendees[0].email }}`
   * **Subject:** `{{ $json.summary }}`
   * **HTML Body:** Use a confirmation email template.

   #### **Node 4: Respond to Webhook**

   * **Response Body**:

     ```json
     {
       "message": "All done! I have scheduled the meeting and sent the confirmation email."
     }
     ```

3. **Connect the Nodes**:

   ```
   Webhook → Google Calendar → Send Email → Respond to Webhook
   ```

4. **Save & Activate** the workflow.

5. Copy the **Production URL** from the Webhook node for later use.

---

### **2. Python Client Setup**

1. **Clone the Repository** or save the script as `main.py`.

2. **Create & Activate a Virtual Environment**:

   ```bash
   python3 -m venv venv
   ```

   **Activate it:**

   * macOS/Linux:

     ```bash
     source venv/bin/activate
     ```
   * Windows:

     ```bash
     .\venv\Scripts\activate
     ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** If PyAudio fails to install on Debian/Ubuntu, run:

   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   ```

4. **Configure the Script**:

   * Open `main.py`.
   * Paste the **Production URL** from your **n8n Webhook** into the `N8N_WEBHOOK_URL` variable.

---

## **Usage**

1. **Start the n8n workflow** (if not already running).
2. **Run the Python script**:

   ```bash
   python3 main.py
   ```
3. The assistant will greet you:
   *"Hello! How can I help you?"*
4. Say:

   ```
   schedule a meeting
   ```
5. Follow the assistant's prompts:

   * Provide guest's email.
   * Provide meeting date.
   * Provide start and end times.
6. Confirm each detail when prompted.
7. Once done, the assistant sends details to **n8n**, schedules the meeting, and sends the confirmation email.
8. To **stop the assistant**, say:

   ```
   stop
   ```

   or

   ```
   goodbye
   ```

---

## **Tech Stack**

* **Python** – Speech recognition & TTS
* **SpeechRecognition** – Convert voice → text
* **pyttsx3** – Convert text → speech
* **PyAudio** – Microphone integration
* **n8n** – Workflow automation
* **Google Calendar API** – Schedule meetings
* **SMTP / Gmail API** – Send confirmation emails

---

## **Future Improvements**

* Add **multi-language support** for voice interactions.
* Enable **rescheduling** and **canceling** meetings via voice.
* Integrate with **Outlook Calendar** and **Microsoft Teams**.

---

## **License**

This project is licensed under the **MIT License**.

---

## **Author**

**Ajoy Das**
💻 Built with Python + n8n
📧 Contact: [ajoyd0957@gmail.com](mailto:ajoyd0957@gmail.com)

```

---

Do you also want me to include a **sample `requirements.txt`** based on the libraries used in this project? It’ll make setup easier and ensure compatibility. Should I?
```
