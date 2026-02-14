# 🧪 RESUME UPLOAD TESTING GUIDE
**Simple Step-by-Step Instructions for Beginners**

---

## 🎬 BEFORE YOU START

### Step 0: Get Your User ID
1. Make sure Flask server is running (in one terminal):
   ```bash
   cd backend
   ..\.venv\Scripts\python.exe app.py
   ```

2. In a NEW terminal, run this command:
   ```bash
   cd backend
   ..\.venv\Scripts\python.exe get_user_id.py
   ```

3. **COPY the User ID** shown on screen (it looks like: `65c9f3a2b1234567890abcde`)

4. **Prepare a resume file**: 
   - Use a real resume in PDF or DOCX format
   - Or download a sample resume from internet
   - Save it on Desktop for easy access

---

## 📱 OPTION 1: Using POSTMAN (EASIEST - Recommended for Beginners!)

### What is Postman?
Think of Postman like a **web browser, but for testing APIs**. Instead of visiting websites, you send data to your backend server.

### Step 1: Download Postman
1. Open browser → Go to: **https://www.postman.com/downloads/**
2. Click **"Download for Windows"** (big blue button)
3. Run the installer → Click Next, Next, Finish
4. Open Postman app

### Step 2: Create New Request
1. Click **"New"** button (top-left corner)
2. Select **"HTTP Request"**
3. You'll see a blank request window

### Step 3: Set Up the Request

**a) Change Method Type:**
   - See the dropdown that says "GET"? Click it
   - Select **"POST"** instead

**b) Enter the URL:**
   - In the URL bar (where it says "Enter URL"), type:
   ```
   http://localhost:5000/api/resume/upload
   ```

**c) Set Up the Body:**
   1. Below the URL bar, click the **"Body"** tab
   2. Select **"form-data"** (radio button)
   3. Now you'll see a table with Key-Value columns

**d) Add Your Data:**
   
   **Row 1: Upload the Resume File**
   - Key: Type `resume`
   - Type: There's a dropdown on the right side of Key field - select **"File"**
   - Value: Click **"Select Files"** button → Choose your resume PDF from Desktop
   
   **Row 2: Add User ID**
   - Key: Type `user_id`
   - Type: Keep it as **"Text"**
   - Value: Paste the User ID you copied from Step 0

### Step 4: Send Request!
1. Click the big blue **"Send"** button (top-right)
2. Wait 2-3 seconds...
3. Scroll down to see the **Response** section

### Step 5: Check the Result
✅ **If Successful**, you'll see:
```json
{
  "message": "Resume uploaded and processed successfully",
  "resume_id": "65c9f3b4...",
  "extracted_skills": ["Python", "JavaScript", "React", ...],
  "confidence": 75.5
}
```

❌ **If Error**, you'll see:
```json
{
  "error": "No file uploaded"
}
```

**Common Errors & Fixes:**
- "No file uploaded" → Make sure you selected "File" type for resume key
- "User not found" → Check if user_id is correct (no extra spaces)
- 404 error → Check if Flask server is running
- 500 error → Check server terminal for error messages

---

## 💻 OPTION 2: Using curl (Command Line - For Advanced Users)

### What is curl?
**curl** is a command-line tool that sends requests from the terminal (like Postman, but without the visual interface).

### Step 1: Open PowerShell
1. Press **Windows Key**
2. Type **"PowerShell"**
3. Click on **"Windows PowerShell"**
4. Navigate to your project folder:
   ```powershell
   cd C:\Users\Asus\OneDrive\Desktop\ai-job-portal-skill-matching
   ```

### Step 2: Prepare Your Command
The curl command has 3 parts:

```powershell
curl -X POST "http://localhost:5000/api/resume/upload" `
  -F "resume=@C:\Users\Asus\Desktop\MyResume.pdf" `
  -F "user_id=YOUR_USER_ID_HERE"
```

**Breaking it down:**
- `curl` = The command we're running
- `-X POST` = Send a POST request (like clicking Submit button)
- `"http://localhost:5000/api/resume/upload"` = Where to send the request
- `-F "resume=@C:\Users\Asus\Desktop\MyResume.pdf"` = Upload this file
  - `resume` = Field name (must be exactly "resume")
  - `@` = Symbol means "upload this file"
  - `C:\Users\Asus\Desktop\MyResume.pdf` = Full path to your resume
- `-F "user_id=YOUR_USER_ID_HERE"` = Your user ID from Step 0
- `` ` `` = Backtick at end of line = Continue command on next line (PowerShell)

### Step 3: Customize the Command
Replace these parts with YOUR values:

1. **Replace the file path:**
   - Change `C:\Users\Asus\Desktop\MyResume.pdf` 
   - To YOUR resume's actual location
   
   **How to get file path?**
   - Right-click your resume file
   - Hold **Shift** key
   - Click **"Copy as path"**
   - Paste it in the command (remove quotes if any)

2. **Replace the user_id:**
   - Change `YOUR_USER_ID_HERE`
   - To the User ID you got from Step 0

### Step 4: Example with Real Values
```powershell
curl -X POST "http://localhost:5000/api/resume/upload" `
  -F "resume=@C:\Users\Asus\Desktop\JohnDoe_Resume.pdf" `
  -F "user_id=65c9f3a2b1234567890abcde"
```

### Step 5: Run the Command
1. Copy the entire command (all 3 lines)
2. Paste in PowerShell
3. Press **Enter**
4. Wait 2-3 seconds for response

### Step 6: Read the Output
You'll see JSON output directly in terminal:
```json
{"message":"Resume uploaded successfully","resume_id":"...","extracted_skills":[...]}
```

---

## 🎯 WHICH METHOD SHOULD I USE?

| Feature | Postman | curl |
|---------|---------|------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Very easy, visual | ⭐⭐ Need to type commands |
| **Best For** | Beginners, testing, debugging | Advanced users, automation |
| **Speed** | Slower (click, click, click) | Faster (one command) |
| **Learning Curve** | 5 minutes | 30 minutes |
| **Recommended For** | **Students, first-time users** | Developers, scripts |

**My Recommendation:** Start with **Postman**! It's much easier to understand and see what's happening.

---

## 🐛 TROUBLESHOOTING

### Problem: "Connection refused" or "Failed to connect"
**Solution:** Flask server is not running!
```bash
# Open a terminal and run:
cd backend
..\.venv\Scripts\python.exe app.py
```

### Problem: "User not found"
**Solution:** Wrong user_id or user doesn't exist in database
```bash
# Create a new user first:
cd backend
..\.venv\Scripts\python.exe test_auth.py
# Copy the user ID from the response
```

### Problem: "No file part in request"
**Solution (Postman):** 
- Make sure you selected **"File"** type (not Text) for resume key
- Make sure key name is exactly `resume` (lowercase)

**Solution (curl):**
- Make sure you have `@` symbol before file path
- Check file path is correct (no typos)

### Problem: "File type not allowed"
**Solution:** Only PDF, DOC, DOCX files are allowed
- Convert your resume to PDF if it's in another format

### Problem: "File too large"
**Solution:** Resume must be under 5MB
- Compress your PDF using online tools

---

## 📸 VISUAL GUIDE (Postman)

**What your Postman screen should look like:**

```
┌─────────────────────────────────────────────────┐
│ POST ▼  http://localhost:5000/api/resume/upload│  [Send]
├─────────────────────────────────────────────────┤
│ Params  Authorization  Headers  Body ◀── Click this
│                                                   
│ ○ none                                           
│ ○ form-data  ◀── Select this                     
│ ○ x-www-form-urlencoded                         
│ ○ raw                                            
│ ○ binary                                         
│                                                   
│ ┌──────────┬────────┬─────────────────┬────┐   
│ │   KEY    │  TYPE  │     VALUE       │    │   
│ ├──────────┼────────┼─────────────────┼────┤   
│ │ resume   │ File ▼ │ [Select Files]  │ ✓  │   
│ │ user_id  │ Text ▼ │ 65c9f3a2b123... │ ✓  │   
│ └──────────┴────────┴─────────────────┴────┘   
│                                                   
└─────────────────────────────────────────────────┘

Response (below):
{
  "message": "Resume uploaded and processed successfully",
  "resume_id": "65c9f3b4c5678901234defgh",
  "extracted_skills": [
    "Python",
    "JavaScript",
    "React",
    "MongoDB",
    "Flask"
  ],
  "confidence": 75.5
}
```

---

## 🎓 NEXT STEPS AFTER TESTING

Once you successfully upload a resume:
1. **Check MongoDB** - Go to MongoDB Atlas, you'll see your resume data
2. **Verify Skills** - Check if the AI extracted skills correctly
3. **Test with Different Resumes** - Try various formats (PDF, DOCX)
4. **Ready for Step 6** - We'll build the Job Posting API next!

---

## 📝 QUICK REFERENCE

**Get User ID:**
```bash
cd backend
..\.venv\Scripts\python.exe get_user_id.py
```

**Start Server:**
```bash
cd backend
..\.venv\Scripts\python.exe app.py
```

**Postman URL:**
```
http://localhost:5000/api/resume/upload
```

**Postman Body (form-data):**
- Key: `resume` | Type: File | Value: [Select your PDF]
- Key: `user_id` | Type: Text | Value: [Your user ID]

**curl Command:**
```powershell
curl -X POST "http://localhost:5000/api/resume/upload" `
  -F "resume=@PATH_TO_YOUR_RESUME.pdf" `
  -F "user_id=YOUR_USER_ID"
```

---

Need help? Check the server terminal for error messages! 🚀
