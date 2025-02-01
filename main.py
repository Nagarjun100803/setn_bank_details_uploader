from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import execute_sql_commands, execute_sql_select_statement
import pandas as pd 
import io
from config import settings
from typing import Literal
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime





app = FastAPI(title = "SETN Bank Detail Handler")
scheduler = BackgroundScheduler()



templates = Jinja2Templates("templates")
app.mount("/static", StaticFiles(directory = "static"), name = "static")



def get_not_uploaded_students():
    sql: str = """
        select
            email_id
        from 
            beneficiaries as be 
        where 
            not exists(
                select 
                    *
                from 
                    bank_details as bd
                where 
                    bd.aadhar_num = be.aadhar_num
            )
    """
    email_ids = execute_sql_select_statement(sql)
    return email_ids


def send_email(recipients: list[str], subject: str):
    """
    Sends an email reminder to upload bank details with a secure link.

    """
    try:
        action_link = f"{settings.base_url}/verify_aadhar"  # Full verification link

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; text-align: center; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50;">⏳ Important Reminder</h2>
                <p style="color: #555; font-size: 16px;">
                    Dear Student, <br><br>
                    We noticed that your bank details are not yet updated. To proceed further with your application, 
                    please upload your bank details at your earliest convenience.
                </p>
                <p style="font-size: 16px; font-weight: bold; color: #333;">
                    Kindly use the link below to complete your bank details submission.
                </p>
                <p>
                    <a href="{action_link}" style="display: inline-block; padding: 12px 20px; background-color: #28a745; 
                    color: white; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                        Upload Bank Details
                    </a>
                </p>
                <p style="color: #777; font-size: 14px;">
                    If you have already completed this step, please ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 14px; color: gray;">Best regards,<br>SETN Team</p>
            </div>
        </body>
        </html>
        """

        msg = EmailMessage()
        msg["From"] = formataddr(("SETN Support", settings.sender_email))
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content("This email requires an HTML viewer.")
        msg.add_alternative(html_content, subtype="html")

        # Sending Email
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()  # Secure connection
            server.login(settings.sender_email, settings.sender_password)
            server.send_message(msg)

        print(f"✅ Email sent to {', '.join(recipients)} with link: {action_link}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")



def send_remainder():

    today = datetime.now().date()
    if today < settings.end_date:
        print("Date is in range send mail")
        
        not_uploaded_students = get_not_uploaded_students()
        
        if not not_uploaded_students:
            print("All Students uploaded their bank details.")
        
        email_ids = list(pd.DataFrame(not_uploaded_students)['email_id'].values)
        
        print(email_ids)
        
        send_email(recipients=email_ids, subject = "Bank Details Upload - Reg")
    else:
        print("Date ended.")

    


# Add a job to scheduler.
scheduler.add_job(send_remainder, trigger = CronTrigger(hour = 17, minute = 0)) # Send a remainder email daily at 5pm.
scheduler.start()




class BankDetails(BaseModel):

    aadhar_num: str
    name_as_in_passbook: str
    account_number: str
    ifsc_code: str
    bank_name: str
    branch: str
    linked_phone_num: str
    account_holder: Literal["Self", "Father", "Mother", "Guardian"]
    upi_id: str | None
    email_id: str


class AdminCredentials(BaseModel):
    username: str 
    password: str



@app.get("/test")
def test_page():
    return "Shivaya Namah"




@app.get("/verify_aadhar")
def get_bank_details_page(request: Request):
    return templates.TemplateResponse("bank_detail_uploader.html", {"request": request})





@app.post("/verify_aadhar")
def check_aadhar_number_existance(
    request: Request,
    aadhar_num: str = Form()
):
    context: dict = {"request": request, "verification_status": False, "entered_aadhar_num": aadhar_num}
    # existing_record = check_aadhar_exists(aadhar_num)

    sql: str = """
        select 
            (    
                select 
                    1 as aadhar_exist
                from 
                    beneficiaries as be 
                where 
                    be.aadhar_num = %(aadhar_num)s
            ),
            (        
                select 
                    1 as bank_detail_exist
                from 
                    bank_details as bd 
                where 
                    bd.aadhar_num = %(aadhar_num)s
            )
    """
    
    existing_record = execute_sql_select_statement(sql, {"aadhar_num": aadhar_num}, fetch_all = False)
    
    if not existing_record["aadhar_exist"]:
        context.update({"message": "Sorry, no record found with this Aadhar Number!"})

    elif existing_record["bank_detail_exist"]:
        context.update({"message": "Oops, You already provided your bank details."})
    
    else:
        context.update({
            "verification_status": True,
            "entered_aadhar_num": aadhar_num,
            "message": "Aadhar Exists"
        })
    
    return templates.TemplateResponse("bank_detail_uploader.html", context)



@app.post("/bank_details")
def create_bank_details(
    request: Request,
    bank_details: BankDetails = Form()
):
    
    context: dict = {"request": request, "message_type": "Info"}
    # Create a new entry.
    create_bank_detail_sql: str = """
        insert into bank_details(
            aadhar_num, name_as_in_passbook, account_number, ifsc_code,
            bank_name, branch, account_holder, linked_phone_num, email_id
        )
        values(
            %(aadhar_num)s, %(name_as_in_passbook)s, %(account_number)s, %(ifsc_code)s,
            %(bank_name)s, %(branch)s, %(account_holder)s, %(linked_phone_num)s, %(email_id)s
        );
    """
    vars = bank_details.model_dump()
    # print(create_bank_detail_sql)
    # print(vars)
    new_record: None = execute_sql_commands(create_bank_detail_sql, vars)
    context.update({"message": "Bank details uploaded successfully."})
    
    return templates.TemplateResponse("message.html", context)


def get_entered_bank_details():

    sql: str = """
        select 
            row_number() over() as id,
            *
        from 
            beneficiaries as b
        join 
            bank_details as bd
        on 
            b.aadhar_num = bd.aadhar_num
    """
    records = execute_sql_select_statement(sql)

    return records


@app.get("/verify_admin")
def get_entered_data(request: Request): 
    return templates.TemplateResponse("view_excel.html", {"request": request})



@app.post("/verify_admin")
def verify_admin_credentials(
    request: Request,
    admin_credentials: AdminCredentials = Form()
):
    # print(admin_credentials)
    context: dict = {"request": request, "admin_verification": False}
    
    if not (
        (admin_credentials.username == settings.admin_username) and
        (admin_credentials.password == settings.admin_password)
    ):
        print(context)
        
        context.update({"message": "Invalid username or password!", "entered_username": admin_credentials.username})
        
        return templates.TemplateResponse("view_excel.html", context)
    

    records = get_entered_bank_details()
    context.update({"admin_verification": True, "records": records})

    return templates.TemplateResponse("view_excel.html", context)
        



@app.get("/download_data")
def download_entered_bank_details(request: Request):

    records = get_entered_bank_details()
    
    if not records:
        return templates.Templateresponse("message.html", {
            "request": request, "message": "Sorry, No records to show",
            "message_type": "Info"
        })
    
    bank_details_df = pd.DataFrame(records)
    
    file = io.BytesIO() # In memory file

    with pd.ExcelWriter(file, engine = "openpyxl") as writer:
        bank_details_df.to_excel(writer, index = False, sheet_name = "sheet1")
    
    # Move the buffer cursor to the beginning
    file.seek(0)

    return StreamingResponse(
        file,
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers = {
            "Content-Disposition": "inline; filename=report.xlsx"
            }
    )



