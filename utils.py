from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from PyPDF2 import PdfReader
import io
import os
from openai import OpenAI
import json
import uvicorn


def pdf_parser(pdf_reader):
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    return text

def make_prompt(criteria, criteria_list, text):
    prompt = f"""
    Analyze the following CV text and categorize the content into the 8 O-1A visa criteria: 
    Awards, Membership, Press, Judging, Original contribution, Scholarly articles, Critical employment, High remuneration. 
    
    For each criteria is described below:
    {criteria_list[0]}: {criteria[criteria_list[0]]}
    {criteria_list[1]}: {criteria[criteria_list[1]]}
    {criteria_list[2]}: {criteria[criteria_list[2]]}
    {criteria_list[3]}: {criteria[criteria_list[3]]}
    {criteria_list[4]}: {criteria[criteria_list[4]]}
    {criteria_list[5]}: {criteria[criteria_list[5]]}
    {criteria_list[6]}: {criteria[criteria_list[6]]}
    {criteria_list[7]}: {criteria[criteria_list[7]]}

    For CV is described below:
    CV: {text}

    Provide a dictionary = 
    {{
        {criteria_list[0]}: <List all the things that the person has done and meet the {criteria_list[0]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[1]}: <List all the things that the person has done and meet the {criteria_list[1]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[2]}: <List all the things that the person has done and meet the {criteria_list[2]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[3]}: <List all the things that the person has done and meet the {criteria_list[3]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[4]}: <List all the things that the person has done and meet the {criteria_list[4]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[5]}: <List all the things that the person has done and meet the {criteria_list[5]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[6]}: <List all the things that the person has done and meet the {criteria_list[6]} criterion of O-1A, leave it None if there is nothing.>,
        {criteria_list[7]}: <List all the things that the person has done and meet the {criteria_list[7]} criterion of O-1A, leave it None if there is nothing.>,
        Overall likelihood: <The likelihood of O1A qualification in low, medium, or high.>
    }}
    """

    return prompt


def client_response(client, prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful O-1A visa qualification assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.5,
    )
    result_text = response.choices[0].message.content.strip()

    return result_text