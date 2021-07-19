from flask import Flask, render_template, request,redirect, send_from_directory
from flask_cors import cross_origin
from PIL import Image
from werkzeug.utils import secure_filename
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'F:\Installed_Software\tesseract.exe'
tessdata_dir_config = '--tessdata-dir r"F:\Installed_Software\tessdata"'
import os
import numpy as np
import textwrap
import re
from fpdf import FPDF
from PyPDF2 import PdfFileWriter,PdfFileReader

UPLOAD_FOLDER = r'\upload_folder'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# initializing flask app object ..
app = Flask(__name__)

@app.route('/')  # main route ..
@cross_origin()
def intro():
   # workingdir = os.path.abspath(os.getcwd())
   # return send_from_directory(workingdir, '1st.pdf')
    return render_template('intro.html')

@app.route('/image_upload',methods=['GET','POST'])
@cross_origin()
def image_upload():
    print("============= 1 ==================")
    try:
        if request.method == "POST":
            file = request.files.getlist('file[]')
            print("=========2============")
            if file:
                print("yes========================")
                for img in file:
                    if img.filename == '':
                        return redirect(request.url)
                    if allowed_file(img.filename):
                        img.save("upload_folder/" + img.filename)
                        print("==========saved file ===========")
                print("====== all files saved =========")

            path = "upload_folder/"
            text = ""
            for root_path, direcs, filenames in os.walk(path):
                for filename in filenames:
                    im = Image.open(path + filename)
                    a = pytesseract.image_to_string(im, lang='eng')
                    text = text + " " + a

            def join1(string):
                line = re.sub('[^a-zA-Z0-9,."'']', ' ', string)
                arr = np.array(line.split())
                arr1 = " ".join(arr)
                wrapper = textwrap.TextWrapper(width=78)
                word_list = wrapper.wrap(text=arr1)
                # print(word_list)
                string1 = "\n".join(word_list)
                return word_list
            text_book = join1(text)

            pdf = FPDF()
            # Add a page
            pdf.add_page()
            # set style and size of font
            # that you want in the pdf
            pdf.set_font("Arial", size=15)
            # create a cell
            for i in text_book:
                pdf.cell(200, 10, txt=i, ln=1, align='L')
            # save the pdf with name .pdf
            pdf.output("pdf_file.pdf")
            print(text_book)

            # remove images from upload folder ======================================
            for root_path, direcs, filenames in os.walk(path):
                for filename in filenames:
                    print(filename)
                    os.remove("upload_folder/" +filename)
            # display pdf in ui ..
            workingdir = os.path.abspath(os.getcwd())
            return send_from_directory(workingdir, 'pdf_file.pdf')
        else:
            print(" ======== Moving in else part ==========")
            return redirect(request.url)
    except:
        raise Exception

@app.route('/delete_pages',methods=['GET','POST'])
@cross_origin()
def delete_pages():
    if request.method == 'POST':
        From = int(request.form.get("From", False))
        To = int(request.form.get("To", False))

        # for deleting the pages from the pdf

        def delete_page(inpdfFilename, outpdfFilename, pages):
            pdfWriter = PdfFileWriter()
            pdfReader = PdfFileReader(inpdfFilename)
            for i in range(pdfReader.getNumPages()):
                if i not in pages:
                    page = pdfReader.getPage(i)
                    pdfWriter.addPage(page)
                with open(outpdfFilename, 'wb') as outpdf:
                    pdfWriter.write(outpdf)

        workingdir = os.path.abspath(os.getcwd())
        inpdfFilename = workingdir + "\\pdf_file.pdf" #'D:\\celebal intern\\3rd.pdf'
        outpdfFilename = workingdir + "\\pdf_file.pdf" #'D:\\celebal intern\\3rd_new.pdf'
        pages = (From-1,To-1)
        delete_page(inpdfFilename, outpdfFilename, pages)

        return render_template('intro.html', text="Page has been deleted Succcesfully" ,check="view")
    else:
        raise Exception

@app.route('/view_pdf',methods=['GET','POST'])
@cross_origin()
def view_pdf():
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        return send_from_directory(workingdir, 'pdf_file.pdf')
    else:
        raise Exception

if __name__ == '__main__':
    # To run on web ..
    #app.run(host='0.0.0.0',port=8080)
    # To run locally ..
    app.run(host='0.0.0.0',debug=True)
