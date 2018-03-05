from flask import Flask
from flask_ask import Ask, statement, question, session

import json
import requests
import time
import unidecode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

#GLOBALS
ingredients = []
recipe = []
currentStep = 0

#Flask App stuff
app = Flask(__name__)
ask = Ask(app, "/alexa_cooks")

#requires that query is a string that returns valid results when searching SeriousEats
#given a query like "apple pie", gets recipie, ingredients
def getRecipies(query):
	print(query)
	query = query.replace(" ", "+") + "+"
	print(query)
	#adding BraveTart to serious eats will force it to look for only baking recipes
	url = "https://www.seriouseats.com/search?term=" + query + "brave+tart&site=recipes"
	print(url)
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	web_bytes = urlopen(req).read()
	#get raw webpage
	webpage = web_bytes.decode('utf-8')
	#format and parse serch results
	#the string "<div class=..." helps us get to the part of the HTML with the recipe
	soup = BeautifulSoup('<div class="metadata">\n<a class="module__link" '+ webpage.split('a class="module__link"', 1)[1], "html.parser")

	#extract relevent links and titles
	links = soup.find_all('a')
	#remove the "see more" link 
	links.pop()
	titles = soup.find_all('h4')

	#just pick first recipe for now....we can add more options later
	title = titles[0].get_text().split("|")[0]
	link = links[0].get('href')
	print(link)

	req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
	web_bytes = urlopen(req).read()
	webpage = web_bytes.decode('utf-8')
	soup = BeautifulSoup(webpage, "html.parser")
	print(soup.title.string)

	#get recipie and ingredients
	global ingredients
	global recipe
	li_tags = soup.find_all('li')

	#loop through relevant HTML tags and get recipe and ingredients
	for tag in li_tags:
		if('class="ingredient" itemprop="ingredients' in str(tag)):
			ingredients.append(tag.get_text())
		if('class="recipe-procedure-text"' in str(tag)):
			recipe.append(tag.get_text().split(None, 1)[1])

	data = {"title": title, "ingredients": ingredients, "recipe": recipe  }
	return data


@app.route('/')
def homepage():
	return "Ayyyyooo"


#START of our Alexa skill
@ask.launch
def startSkill():
	greeting =  "Welcom to Alexa Cooks, you can ask me for recipes. What would you like to bake?"
	return question(greeting)


#Trigger this function with: "Search for <query> recipes
@ask.intent("SearchRecpieIntent")
def queryRecipies(RecpieQuery):
	recipieData = getRecipies(RecpieQuery)
	response = "I found " + recipieData["title"] + ". " + " Would you like to try it?"
	return question(response)

@ask.intent("AMAZON.NextIntent")
def nextStep():
	global recipe
	global currentStep
	currentStep += 1
	step = recipe[currentStep]
	return statement(step)

@ask.intent("AMAZON.PreviousIntent")
def previousStep():
	global recipe
	global currentStep
	currentStep -= 1
	step = recipe[currentStep]
	return statement(step)

@ask.intent("AMAZON.RepeatIntent")
def repeatStep():
	global recipe
	return statement(recipe[currentStep])

if __name__ == "__main__":
	app.run(debug=True)













