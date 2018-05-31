import os
import csv
from datetime import datetime
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def get_compressed_file(csv_path):
        os.chdir(csv_path)
        os.system("rm *.tar.gz")
        gz_file = 'HC_PUNJAB-HARYANA_%s.tar.gz' % str(datetime.now().date().strftime('%d%m%Y'))
        gz_cmd = 'tar -czf %s *' % gz_file
        os.system(gz_cmd)
        return gz_file

def send_mail(csv_path):
        try:
            #recievers_list = ['delivery@headrun.com', 'sathwick@headrun.com']
            recievers_list = ['akram@headrun.com']
            sender, receivers = 'headrunkpmgproject@gmail.com', ','.join(
                recievers_list)
            ccing = []
            #ccing = ['aravind@headrun.com',
            #         'raja@headrun.com', 'jaideep@headrun.com', 'akram@headrun.net']
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'HC Punjab & Haryana : Run on %s' % (
                str(datetime.now().date()))
            mas = '<h3>Hi Team,</h3>'
            mas += '<p>Please find the High Court of Punjab and Haryana data in the below attachment</p>'
            mas += '<table  border="1" cellpadding="0" cellspacing="0" >'
            mas += '<tr><th>Keyword</th><th>File name</th><th> Number of records</th>'
            gb_file = get_compressed_file(csv_path)
            for csvfile in os.listdir(csv_path):
                if csvfile.endswith('.csv'):
                    no_of_records = len(list(csv.reader(open(csvfile, "r+"))))-1
                    mas += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                        csvfile.split('_')[0].replace('-', ' '), csvfile, no_of_records)
            mas += '</table>\n\n\n'
            mas += '<br>Note : No of records with 0\
         indicates no results for that particular keyword.'
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(gb_file, "rb").read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition', 'attachment', filename=gb_file)
            msg.attach(part)
            msg['From'] = sender
            msg['To'] = receivers
            msg['Cc'] = ",".join(ccing)
            tem = MIMEText(''.join(mas), 'html')
            msg.attach(tem)
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, 'Hkpmgprj')
            total_mail = (recievers_list) + ccing
            server.sendmail(sender, (total_mail), msg.as_string())
            server.quit()
        except Exception as error:
            logging.exception(error)




class PunjabHCWrapper(object):

    def __init__(self):
		self.main_path = os.path.dirname(os.getcwd())
		self.csv_path = os.path.join(os.getcwd(), 'csv_files', datetime.now().strftime('%Y-%m-%d'))

    def main(self):
        file_name = 'inputs.txt'
        mydir = self.csv_path

        if not os.path.isdir(mydir):
            os.makedirs(mydir)
        if os.path.isfile(file_name):
            with open(file_name, 'r') as files:
                rows = files.readlines()
		for row in rows:
			row = row.replace('\r\n', '').strip()
			word, from_date, to_date = row.split('|')
			cmd = "scrapy runspider punjab_highcourt.py -a keyword='%s' -a from_date='%s' -a to_date='%s' -a path='%s'"%(word.strip(), from_date.strip(), to_date.strip(), self.csv_path)
			os.system(cmd)
            send_mail(self.csv_path)
        else:
            logging.exception('Please Specify the input file location properly')


if __name__ == '__main__':
    PunjabHCWrapper().main()
