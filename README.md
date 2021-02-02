# eCommerce_Chatbot-Rasa_Python


# e-Commerce Chatbot in Python
Repo for the Chatbot (Virtual Assistant) implemented in Rasa and Python, which automates the customer service of an e-commerce website.

* Possibility for the user to get from the chatbot:
	* answers to questions about the company and its services
	* additional information about the products sold by the company
	* a change in his account information such as the first name used on the website, phone number and email address
* Possibility for the user to make requests directly through the chatbot, such as:
	* sending a request directly to the company's customer service department so that it can be processed at a later date
	* suggesting a new product the company should sell on the website
	* providing a feedback regarding his chat experience at the end of each conversation
* Designed 22 conversation scenarios based on the writing of 2211 examples of user intents as NLU training data and 768 chatbot responses in English on the Rasa framework
* Used Rasa Open Source for the chatbot architecture
* Used Rasa Action Server to execute "custom actions" allowing the chatbot to validate forms and query a MySQL database
* Integrated the chatbot on a local copy of the e-commerce website as a rest API using the Webchat plugin in JavaScript

![](https://github.com/Zaamine/Zaamine/blob/main/images/rasa_chatbot-screenshot_1.PNG)
![](https://github.com/Zaamine/Zaamine/blob/main/images/rasa_chatbot-screenshot_2.PNG)

The idea behind the codes I uploaded in this repo is to show you what are the important aspects to take into account in order to concretely implement a Chatbot in Rasa and Python, so it helps you implement your very own version of it. It's not about just cloning the repo. The project presented here actually required 4 months of research and work during my second internship assignment in Data Science at Deutsche Telekom, so I only shared the main points.
