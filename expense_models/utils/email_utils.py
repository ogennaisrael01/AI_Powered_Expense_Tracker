from django.core.mail import send_mail
from expense_tracker.settings import EMAIL_HOST_USER, APP_NAME, TOKEN_EXPIRY

def send_email_notification(subject, message, email):
    try:
        email_notif = send_mail(
            subject=subject,
            message=message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[email]
        )

        if email_notif:
            return {"success": True, "message": "Email sent successfully"}
    except OSError as e:
        return {"success": False, "message": f"Network Error, check your network: {e}"}
    except Exception as e:
        return {"success": False, "messae": f"Email service unavailable: {e}"}

app_name = APP_NAME
def account_verification_email(user, link:str) -> tuple:
    subject = "Account verification"
    body =  f"""\
                Hey {user}, Welcome to {app_name}.\n\
                Please use this link to activate your account \n\
                {link}\n
                Dont disclose this with any one else, this is yours.\n\
                
                Link expires in {TOKEN_EXPIRY} MINUTES\n\

                
                Regards {app_name} Team.
            """
    return  subject, body


def reset_password_email(user, link:str) -> tuple:
    subject = "Reset password"
    body = f"""\
            Hey {user}, You requested for password reset. \n\
            Use this link and reset your password \n\
            {link}\n
            Ignore this message is you didn't request for password reset.\n\

            Link expires in {TOKEN_EXPIRY} MINUTES\n\

            Regards {app_name} Team
            """
    return subject, body


def password_reset_successful(user: str) -> tuple:
    subject="password confirmation"
    body=f"""\
            Hey {user}, Your password has been reset sucessfully, you may now proceed to login. \n\n\
            Thanks for using {app_name}\n\
            Regards {app_name} Team
        """
    return subject, body

def withdrawal_email(email, refrence, date, amount, currency):
    subject = f"Reciept for {email}[{refrence}]"
    body = f"""\
            Test Transaction, No real money was sent to you \n\n\
                
            CREDITED \n\n\
                {currency} {amount} \n\n\
            Transaction Details \n\n\
            
            Refrence                    {refrence}\n\
            Date                        {date}   \n\n\
                
            @{app_name} inc 2025\n\
            Payments of Africa
        """
    return subject, body




