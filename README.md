<p align="center">
    <img src="https://github.com/user-attachments/assets/bc5d0500-39c6-4508-8b24-6662212b78f5" alt="VITRA Cobra Mascot" width="400" style="border-radius: 10px;" />
</p>
 
# What is Nova?
**Nova** is an automated OSINT-driven wordlist generation tool built for professional penetration testers seeking to optimize and streamline the credential brute-forcing phase of an engagement. Designed with flexibility, speed, and precision in mind, Nova runs in Linux environments and is written in Python. 

Nova automates the discovery and extraction of publicly available data related to a target—such as names, usernames, company affiliations, locations, dob, workplaces, and other identity markers—through advanced Bing dorking techniques. This data is then parsed,and transformed into highly customized username and password wordlists that follow industry-recognized credential creation patterns.

These curated wordlists are designed to integrate directly with tools like Hydra and John the Ripper, increasing success rates during brute-force or password spraying attacks.

# Requirements
- OS: Any Linux distribution (preferably Kali or Parrot OS) 
- 4 GB RAM
- 80 GB Hard Drive
  
# ⚒️ Installation
The first step you must perform is:
- Deploy a Virtual Machine (Linux distribution)
  
- Clone Github Repository:
```bash
git clone https://github.com/username/Nova.git
```
- Install dependencies - requests and beautifulsoup4:
```bash  
pip install requests
pip install beautifulsoup4
```
The rest of the dependencies are part of Python's standard library.

For the best results, execute Nova as the user "kali" and keep the file on your desktop.
# Instructions
**Navigate to the Project Directory**:
```bash
cd <project directory>
```
**Execute the main.py**:
```bash
sudo python3 main.py
```
**Provide Input**:
- After execution, you will be prompted with five input fields:
1. Target's Full Name (required): Enter the target's full or partial name.
2. Target's Date Of Birth (optional): Enter the target's DOB (yyyy or MM/DD/YYYY).
3. Target's Company Name (optional): Enter the name of the company where the target is employed.
4. Target's Location (optional): Enter the target's city or location.
5. Desired Wordlist Size (required): Enter the desired wordlist size (500, 1000, 5000).
![image](https://github.com/user-attachments/assets/96d9e7e7-07a2-4ad4-bf32-951142d5f907)

**Monitor Progress**:
- The program will execute and display execution processes for each script until the final script is completed.
![image](https://github.com/user-attachments/assets/5abe6cba-f076-4bd0-a147-ba1acda043d5)

**Generate Report**:
- Upon completion, the program will generate two .txt files, one containing usernames and the other passwords.
