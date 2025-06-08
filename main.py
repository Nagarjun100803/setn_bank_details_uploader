from fastapi import FastAPI, Request, Form, Response, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, constr
from database import execute_sql_commands, execute_sql_select_statement
import pandas as pd 
import io
from config import settings
# from typing import Literal, Optional
# import smtplib
# from email.message import EmailMessage
# from email.utils import formataddr
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime





app = FastAPI(title = "SETN Bank Detail Handler")
# scheduler = BackgroundScheduler()



templates = Jinja2Templates("templates")
app.mount("/static", StaticFiles(directory = "static"), name = "static")



# def get_not_uploaded_students():
#     sql: str = """
#         select
#             email_id
#         from 
#             beneficiaries as be 
#         where 
#             not exists(
#                 select 
#                     *
#                 from 
#                     bank_details as bd
#                 where 
#                     bd.email_id = be.email_id
#             )
#     """
#     email_ids = execute_sql_select_statement(sql)
#     return email_ids


# def send_email(recipients: list[str], subject: str):
#     """
#     Sends an email reminder to upload bank details with a secure link.

#     """
#     try:
#         action_link = f"https://setn-bank-details-uploader-app.onrender.com/verify_email"  # Full verification link

#         # html_content = f"""
#         #     <html>
#         #     <body style="font-family: Arial, sans-serif; background: linear-gradient(to bottom right, #d1fae5, #fde68a); padding: 20px; text-align: center;">
#         #         <div style="max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 12px rgba(0,0,0,0.1);">
#         #             <h1 style="text-decoration: underline; font-size: 22px; color: #2c3e50;">Dear Student</h1>
#         #             <p style="font-size: 16px; color: #444; text-align: justify; line-height: 1.5;">
#         #                 As per the instructions on our SETN Scholarship Application form, many students have submitted their bank details by email to 
#         #                 <span style="color: #6366f1; font-weight: bold; text-decoration: underline;">souengrs@gmail.com</span>. 
#         #                 However, we are finding it difficult to link the bank details to the respective students.
#         #             </p>
#         #             <p style="font-size: 16px; color: #444; text-align: justify; line-height: 1.5;">
#         #                 Hence the beneficiary students are requested to update their bank details on our portal by clicking the following link:
#         #             </p>
#         #             <p>
#         #                 <a href="{action_link}" style="display: inline-block; padding: 12px 24px; background-color: #10b981; 
#         #                 color: white; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
#         #                     Update Bank Details
#         #                 </a>
#         #             </p>
#         #             <div style="text-align: right; margin-top: 20px; color: #333; font-weight: bold;">
#         #                 <p>Thanks,</p>
#         #                 <p>Er KB Neelakantan</p>
#         #                 <p style="text-decoration: underline;">9840892220</p>
#         #                 <p>Er SR Balasubramanian</p>
#         #                 <p style="text-decoration: underline;">9629339454</p>
#         #                 <p style="font-size: 14px;">Co-Founders, SETN</p>
#         #             </div>
#         #         </div>
#         #     </body>
#         #     </html>
#         # """ 
        

#         # html_content = """
#         #         <!DOCTYPE html>
#         #         <html>
#         #         <head>
#         #             <meta name="viewport" content="width=device-width, initial-scale=1">
#         #             <style>
#         #                 body {
#         #                     font-family: Arial, sans-serif;
#         #                     line-height: 1.6;
#         #                     margin: 0;
#         #                     padding: 20px;
#         #                     background-color: #f4f4f4;
#         #                 }
#         #                 .container {
#         #                     max-width: 600px;
#         #                     margin: auto;
#         #                     background: #fff;
#         #                     padding: 20px;
#         #                     border-radius: 8px;
#         #                     box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
#         #                 }
#         #                 h2 {
#         #                     color: #333;
#         #                 }
#         #                 p {
#         #                     color: #555;
#         #                 }
#         #                 .link-button {
#         #                     display: inline-block;
#         #                     background-color: #007bff;
#         #                     color: #fff;
#         #                     padding: 10px 20px;
#         #                     text-decoration: none;
#         #                     border-radius: 5px;
#         #                     font-size: 16px;
#         #                     margin-top: 10px;
#         #                 }
#         #                 .important-note {
#         #                     margin-top: 20px;
#         #                     padding: 10px;
#         #                     background-color: #ffeeba;
#         #                     border-left: 5px solid #ff9800;
#         #                     font-weight: bold;
#         #                     color: #333;
#         #                 }
#         #                 .important-note p {
#         #                     margin: 5px 0;
#         #                 }
#         #                 .footer {
#         #                     margin-top: 20px;
#         #                     font-size: 14px;
#         #                     color: #777;
#         #                 }
#         #             </style>
#         #         </head>
#         #         <body>

#         #         <div class="container">
#         #             <h2>Dear Student,</h2>
#         #             <p>Please submit your bank details immediately (before <strong>2nd March 2025</strong>) through the link provided below. If it is submitted using any other mode, it will not be considered.</p>
                    
#         #             <p><strong>Submit your details here:</strong></p>
#         #             <a href="https://setn-bank-details-uploader-app.onrender.com/verify_email" class="link-button">Click Here</a>
                    
#         #             <div class="important-note">
#         #                 <p>⚠️ <strong>Important:</strong></p>
#         #                 <p>Do <strong>NOT</strong> send your bank details by replying to this email or through any other means.</p>
#         #                 <p>If the bank details are not received through this portal on or before <strong>March 2, 2025</strong>, the scholarship will <strong>not</strong> be paid for this semester.</p>
#         #             </div>
                    
#         #             <div class="footer">
#         #                 <p>Co-Founders, SETN</p>
#         #                 <p><strong>K B Neelakantan</strong><br>📞 9840892220</p>
#         #                 <p><strong>S R Balasubramanian</strong><br>📞 9629339454</p>
#         #             </div>
#         #         </div>

#         #         </body>
#         #         </html>
#         # """

#         html_content = """
            
#             மிகவும் அவசரம் – உங்கள் வங்கி விவரங்களை உடனே வழங்குங்கள்

#             அன்புள்ள மாணவரே,

#             உங்கள் SETN உதவித்தொகை பெற, உங்கள் வங்கி விவரங்கள் அவசியமாக தேவை.

#             கடைசி நாள்: 17-3-2025 (திங்கட்கிழமை).
#             இந்த தேதிக்குள் உங்கள் விவரங்களைச் சமர்ப்பிக்கத் தவறினால், உங்கள் பெயர் நீக்கப்படும், மேலும் உதவித்தொகை வழங்கப்படமாட்டாது.

#             உங்கள் வங்கி விவரங்களை வழங்க, கீழே உள்ள லிங்கை கிளிக் செய்யவும்:
#             https://setn-bank-details-uploader-app.onrender.com/verify_email

#             வங்கி விவரங்களை வழங்காத மாணவர்களுக்கு உதவித்தொகை வழங்க முடியாது.

#             நன்றி,
#             Er. K B நீலகண்டன் – 9840892220
#             Er. S R பாலசுப்ரமணியன் – 9629339454
#             Co-Founders, SETN

#             -----

#             Subject: Urgent – Submit Your Bank Details for SETN Scholarship

#             Dear Student,

#             Your bank details are required to process your SETN scholarship.

#             Last date: 17-3-2025 (Monday).
#             If you fail to submit your details by this date, your name will be removed, and the scholarship money will not be transferred.

#             Click the link below to submit your bank details:
#             https://setn-bank-details-uploader-app.onrender.com/verify_email


#             Students who do not submit their bank details will not receive the scholarship.

#             Thanks,
#             K B Neelakantan – 9840892220
#             S R Balasubramanian – 9629339454
#             Co-Founders, SETN



#         """
#         msg = EmailMessage()
#         msg["From"] = formataddr(("SETN Support", settings.sender_email))
#         msg["To"] = ", ".join(recipients)
#         msg["Subject"] = subject
#         msg.set_content("This email requires an HTML viewer.")
#         msg.add_alternative(html_content, subtype="html")

#         # Sending Email
#         with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
#             server.starttls()  # Secure connection
#             server.login(settings.sender_email, settings.sender_password)
#             server.send_message(msg)

#         print(f"✅ Email sent to {', '.join(recipients)} with link: {action_link}")

#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")



# def send_remainder():

#     today = datetime.now().date()
#     if today < settings.end_date:
#         print("Date is in range send mail")
        
#         not_uploaded_students = get_not_uploaded_students()
        
#         if not not_uploaded_students:
#             print("All Students uploaded their bank details.")
#             return 
        
#         email_ids = list(pd.DataFrame(not_uploaded_students)['email_id'].values)
        
#         print(f"There are {len(email_ids)} beneficiaries not uploaded their bank details and the email ids are -> {email_ids}")
        
#     else:
#         print("Date ended.")

    


# # Add a job to scheduler.
# scheduler.add_job(send_remainder, trigger = CronTrigger(hour = 17, minute = 0)) # Send a remainder email daily at 5pm.
# scheduler.start()




# class BankDetails(BaseModel):

#     email_id: str
#     name_as_in_passbook: str
#     account_number: str
#     ifsc_code: str
#     bank_name: str
#     branch: str
#     linked_phone_num: str
#     account_holder: Literal["Self", "Father", "Mother", "Guardian"]
#     upi_id: str | None
#     upi_num: str
#     fee_per_sem: int
    


class StudentBankDetails(BaseModel):
    email_id: EmailStr
    mobile_number: constr(min_length=10, max_length=15) #type: ignore;
    aadhaar_number: constr(min_length=12, max_length=12)
    full_name: str
    account_holder: str
    account_holder_name: str
    account_number: constr(min_length=5)
    ifsc_code: constr(min_length=11, max_length=11)
    bank_name: str
    bank_branch_address: str
    bank_mobile_number: constr(min_length=10, max_length=15)
    upi_number: str | None = None
    semester_fee: float | None = None
    passbook_scan: UploadFile

    
class AdminCredentials(BaseModel):
    username: str 
    password: str



@app.get("/test")
def test_page():
    return "Shivaya Namah"



@app.get("/account")
def get_bank_details_page(request: Request):
    return templates.TemplateResponse("bank_details_uploader.html", {"request": request})

@app.post("/account")
async def add_bank_details(
    request: Request,
    bank_details: StudentBankDetails = Form()
):
 
    context: dict = {"request": request}

    # check the student already upload his/her bank details using email id.
    email_exist_check_sql: str = "select 1 from student_bank_details where email_id = %(email_id)s"
    existing_record = execute_sql_select_statement(email_exist_check_sql, {"email_id": bank_details.email_id}, fetch_all = False)

    if existing_record:
        context.update({
            "message": "You already provided your bank details", 
            "message_type": "Info"
        }) 
        return templates.TemplateResponse("message.html", context)
    
    # Read the pdf file. 

    passbook_data_content: bytes = await bank_details.passbook_scan.read()
    
    # Insert the bank details into the database.
    insert_bank_details_sql: str = """
        insert into student_bank_details(
            email_id, mobile_number, aadhaar_number, full_name,
            account_holder, account_holder_name, account_number,
            ifsc_code, bank_name, bank_branch_address, bank_mobile_number,
            upi_number, semester_fee, passbook_scan
        )
        values(
            %(email_id)s, %(mobile_number)s, %(aadhaar_number)s, %(full_name)s,
            %(account_holder)s, %(account_holder_name)s, %(account_number)s,
            %(ifsc_code)s, %(bank_name)s, %(bank_branch_address)s, %(bank_mobile_number)s,
            %(upi_number)s, %(semester_fee)s, %(passbook_scan)s
        );
    """
    vars = bank_details.model_dump(exclude = {"passbook_scan"})
    
    vars.update({"passbook_scan": passbook_data_content, "semester_fee": bank_details.semester_fee})

    new_record: None = execute_sql_commands(insert_bank_details_sql, vars)
    context.update({"message": "Bank details uploaded successfully."})

    return templates.TemplateResponse("message.html", context)


# @app.get("/verify_email")
# def get_bank_details_page(request: Request):
#     return templates.TemplateResponse("bank_detail_uploader.html", {"request": request})





# @app.post("/verify_email")
# def check_aadhar_number_existance(
#     request: Request,
#     email_id: str = Form()
# ):
#     context: dict = {"request": request, "verification_status": False, "entered_email_id": email_id}


#     sql: str = """
#         select 
#             (    
#                 select 
#                     1 as email_exist
#                 from 
#                     beneficiaries as be 
#                 where 
#                     be.email_id = %(email_id)s
#             ),
#             (        
#                 select 
#                     1 as bank_detail_exist
#                 from 
#                     bank_details as bd 
#                 where 
#                     bd.email_id = %(email_id)s
#             )
#     """
    
#     existing_record = execute_sql_select_statement(sql, {"email_id": email_id}, fetch_all = False)
    
#     if not existing_record["email_exist"]:
#         context.update({"message": "Sorry, no record found with this Email Id!"})

#     elif existing_record["bank_detail_exist"]:
#         context.update({"message": "Oops, You already provided your bank details."})
    
#     else:
#         context.update({
#             "verification_status": True,
#             "message": "Email exists"
#         })
    
#     return templates.TemplateResponse("bank_detail_uploader.html", context)



# @app.post("/bank_details")
# def create_bank_details(
#     request: Request,
#     bank_details: BankDetails = Form()
# ):
#     context: dict = {"request": request, "message_type": "Info"}
    
#     # Check if the record already exists with the email_id

#     sql: str = """
#         select 
#             *
#         from 
#             bank_details
#         where 
#             email_id = %(email_id)s
#     """
#     vars = {"email_id": bank_details.email_id}

#     exisiting_record = execute_sql_select_statement(sql, vars, fetch_all = False)

#     if exisiting_record:
#         context.update({"message": "Oops, You already provided your bank details."})
#         return templates.TemplateResponse("message.html", context)
    
#     # Create a new entry.
#     create_bank_detail_sql: str = """
#         insert into bank_details(
#             name_as_in_passbook, account_number, ifsc_code,
#             bank_name, branch, account_holder, linked_phone_num, email_id,
#             upi_num, upi_id, fee_per_sem, created_at
#         )
#         values(
#             %(name_as_in_passbook)s, %(account_number)s, %(ifsc_code)s,
#             %(bank_name)s, %(branch)s, %(account_holder)s, %(linked_phone_num)s, %(email_id)s,
#             %(upi_num)s, %(upi_id)s, %(fee_per_sem)s, %(created_at)s
#         );
#     """
#     vars = bank_details.model_dump()
#     vars.update({"created_at": "now()"})
#     # print(create_bank_detail_sql)
#     # print(vars)
#     new_record: None = execute_sql_commands(create_bank_detail_sql, vars)
#     context.update({"message": "Bank details uploaded successfully."})
    
#     return templates.TemplateResponse("message.html", context)


def get_entered_bank_details():

    # Select all the bank details except passbook.
    sql: str = """
        select 
            email_id, mobile_number, aadhaar_number, full_name,
            account_holder, account_holder_name, account_number,
            ifsc_code, bank_name, bank_branch_address, bank_mobile_number,
            upi_number, semester_fee, created_at
        from 
            student_bank_details
        ;
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
        # print(context)
        
        context.update({"message": "Invalid username or password!", "entered_username": admin_credentials.username})
        
        return templates.TemplateResponse("view_excel.html", context)
    

    records = get_entered_bank_details()
    context.update({"admin_verification": True, "records": records})

    return templates.TemplateResponse("view_excel.html", context)
        

@app.get("/book")
def bank_passbook(
    request: Request,
    email_id: EmailStr
):
    # Fetch passbook data and return it as Response in  pdf format.
    sql: str = "select full_name, passbook_scan from student_bank_details where email_id = %(email_id)s"
    record = execute_sql_select_statement(sql, {"email_id": email_id}, fetch_all = False)

    if not record:
        return templates.TemplateResponse("message.html", {
            "request": request, "message": "No passbook found for this email id",
            "message_type": "Info"
        })

    return Response(content=record["passbook_scan"], media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename={record['full_name']}_passbook.pdf"
    })


@app.get("/download_data")
def download_entered_bank_details(request: Request):

    records = get_entered_bank_details()
    
    if not records:
        return templates.TemplateResponse("message.html", {
            "request": request, "message": "Sorry, No records to show",
            "message_type": "Info"
        })

    def clean_dataframe(df):
        """Clean the DataFrame by removing non-printable characters from string columns."""
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).replace(
                r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', regex=True
            )
        return df
    
    bank_details_df = pd.DataFrame(records)
    bank_details_df = clean_dataframe(bank_details_df)

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


# @app.get("/send_email_remainder")
# def send_email_manually():
#     """Helper function will be used when the scheduler is not working."""
#     # send_email(recipients=["nagarjunramakrishnan10@gmail.com"], subject = "Bank details upload-reg")
#     pending_students_list = pd.DataFrame(get_not_uploaded_students())["email_id"].values
#     batch: int = 50 

#     # print("Total Students", len(pending_students_list))
#     j = 1
#     for i in range(0, len(pending_students_list), batch):
#         student_batch_list = pending_students_list[i : i + batch]
        
#         # print(i, len(student_batch_list), student_batch_list[0])
#         # Send email to the batch
#         send_email(recipients= list(student_batch_list), subject="Bank details upload-reg")
#         print(f"email sent to batch {j} that contains {len(student_batch_list)}")
#         j += 1
    
#     return {"message": "Reminder emails sent in batches"}

    



