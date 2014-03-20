#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup as Soup
import cookielib, urllib2, urllib
import urls
import re
import requests
from datetime import *

def students(config, letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Z", "Æ", "Ø", "Å", "?"]):
    studentList = []

    # Loop through all the letters
    for letter in letters:
        url = urls.students.replace("{{SCHOOL_ID}}", config["school_id"]).replace("{{FIRST_LETTER}}", letter).replace("{{BRANCH_ID}}", config["branch_id"])

        # Sorting settings
        settings = {
            "m%24ChooseTerm%24term" : str(datetime.strftime(datetime.now(), "%Y")),
        }

        # Insert User-agent headers and the cookie information
        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1665.2 Safari/537.36",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Host" : "www.lectio.dk",
            "Origin" : "https://www.lectio.dk"
        }

        response = requests.post(url, data={}, headers=headers)

        html = response.text

        soup = Soup(html)

        studentRows = soup.find("table", attrs={"id" : "m_Content_contenttbl"}).findAll("a")

        for student in studentRows:
            # Define the different name patters
            patterns = [
                r"(?P<name>.*) \((?P<class>.*) (?P<class_student_id>.*)\)",
                r"(?P<name>.*) \((?P<class>.*), (?P<year>.*) (?P<class_description>.*), (?P<status>.*)\)",
                r"(?P<name>.*) \((?P<organization>.*), (?P<class>.*) (?P<status>.*)\)",
                r"(?P<name>.*) \((?P<class_number>.*) (?P<class>.*) (?P<class_student_id>[0-9]*)\)"
            ]

            # Check if the patterns matches
            for pattern in patterns:
                prog = re.compile(pattern)
                if prog.match(student.text):
                    studentInformation = prog.match(student.text)

            # Get the matched regex groups
            groups = studentInformation.groupdict()

            if "class" in groups:
                if "class_number" in groups:
                    studentClass = "%s %s" % (studentInformation.group("class_number"), studentInformation.group("class"))
                else:
                    studentClass = studentInformation.group("class")
            else:
                studentClass = ""

            urlProg = re.compile(r"/lectio/(?P<school_id>[0-9].*)/SkemaNy.aspx?type=(?P<type_name>.*)&elevid=(?P<student_id>.*)")
            urlGroups = urlProg.match(student["href"])

            # Append the student information
            studentList.append({
                "context_card_id" : student["lectiocontextcard"],
                "student_id" : urlGroups.group("student_id") if "student_id" in groups else "",
                "name" : studentInformation.group("name") if "name" in groups else "",
                "class_name" : studentClass,
                "class_student_id" : studentInformation.group("class_student_id") if "class_student_id" in groups else "",
                "class_description" : studentInformation.group("class_description") if "class_description" in groups else "",
                "status" : studentInformation.group("status") if "status" in groups else "",
                "school_id" : config["school_id"],
                "branch_id" : config["branch_id"],
                "type" : urlGroups.group("type_name") if "type_name" in urlGroups else ""
            })

    return {
        "status" : "ok",
        "students" : studentList
    }