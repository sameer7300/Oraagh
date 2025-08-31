import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    try:
        # SMTP settings
        smtp_server = "mail.oraagh.com"
        smtp_port = 465
        username = os.getenv('EMAIL_HOST_USER')
        password = os.getenv('EMAIL_HOST_PASSWORD')
        
        print(f"Testing connection to {smtp_server}:{smtp_port}")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
        
        # Create SMTP connection
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Enable debug output
        
        # Login
        server.login(username, password)
        print("✅ SMTP Authentication successful!")
        
        # Send test email
        msg = MIMEText("Test email from ORAAGH")
        msg['Subject'] = 'SMTP Test'
        msg['From'] = username
        msg['To'] = username  # Send to self
        
        server.send_message(msg)
        print("✅ Test email sent successfully!")
        
        server.quit()
        
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

if __name__ == "__main__":
    test_smtp_connection()
