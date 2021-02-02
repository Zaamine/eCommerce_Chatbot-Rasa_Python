# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
import re
import mysql.connector
import urllib.request
import urllib.parse

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

""" Fonction used to extract the metadata sent using the "customData" parameter through webchat """
def extract_metadata_from_tracker(tracker):
    events = tracker.current_state()['events']
    user_events = []
    for e in events:
        if e['event'] == 'user':
            user_events.append(e)

    return user_events[-1]['metadata']


""" Fonction used to check if the user is logged in to his account or not based on the "session_userId" value in the metadata sent through webchat """
class CheckIfUserIsLoggedIn(Action):
    def name(self) -> Text:
        return "action_checkIfUserIsLoggedIn"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # extract the metadata into a dictionnary type variable
        customDataDict = extract_metadata_from_tracker(tracker)

        # select the "session_userId" value from the metadata dictionnary extracted
        session_idUtilisateur = customDataDict["session_userId"]

        # set the "userIsNotLoggedIn" slot or the "userIsLoggedIn" slot in Rasa domain, according to the value extracted from the metadata
        if session_idUtilisateur == "userIsNotLoggedIn":
            return [SlotSet("userIsNotLoggedIn", "userIsNotLoggedIn")]
        else:
            return [SlotSet("userIsLoggedIn", "userIsLoggedIn")]


""" Fonction used to insert a custom feedback given by the end-user into the database """
class InsertNewFeedback(Action):
    def name(self) -> Text:
        return "action_insertNewFeedback"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # database connection parameters
        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        # connect to the database, using a prepared statement in order to prevent from potential SQL injections
        linkCursor = link.cursor(prepared=True)

        # sql query/statement we to pass on
        stmt = "INSERT INTO FeedbackEcommerce (feedbackText) VALUES (?)"

        # extract the "otherFeedback" slot from Rasa domain
        feedbackText = tracker.get_slot("otherFeedback")

        # execute the prepared statement
        linkCursor.execute(stmt, (feedbackText, ))

        # commit the current transaction for the specified database connection
        # it is required to make the changes, otherwise no changes are made to the table
        link.commit()

        # display a chatbot utterance/response
        dispatcher.utter_message(text="Thanks for the feedback!")

        # this function doesn't need to return anything, every actions were already done during its execution
        return []


""" Fonction used to validate the "searchedProducts_form" """
class ValidateSearchedProductsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_searchedProducts_form"

    def validate_searchedProducts(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        # retrieve the current slot value, which is "searchedProducts"
        searchedProducts = slot_value

        # verify that the end-user has only typed letters when searching for his product
        if searchedProducts.isalpha():

            # the end-user has to write in the chat at least 3 letters to search for the product he wants
            if len(searchedProducts) >= 3:
                # validation succeeded, set the value of the "searchedProducts" slot to value given by user
                return {"searchedProducts": slot_value}
            else:
                # validation failed, set this slot to None so that the user will be asked for the slot again
                dispatcher.utter_message(
                    text="Your product search must contain at least 3 letters.")
                return {"searchedProducts": None}
        else:
            # validation failed, set this slot to None so that the user will be asked for the slot again
            dispatcher.utter_message(
                text="Please type only letters for your product search.")
            return {"searchedProducts": None}


""" Fonction used to select the right product information in the database, when the searchedProducts_form is validated """
class SelectProductInformation(Action):
    def name(self) -> Text:
        return "action_selectProductInformation"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        linkCursor = link.cursor(prepared=True)
        stmt = "SELECT productWording, productDescription, productStock, unitPrice FROM ProductEcommerce WHERE productWording like ?"
        searchedProducts = tracker.get_slot("searchedProducts")

        # string concatenation with "%" in order to search for products that contains in their labels the "searchedProducts" slot
        searchedProductsWording = "%" + searchedProducts + "%"
        linkCursor.execute(stmt, (searchedProductsWording, ))

        # store all the results from the sql query in the "stmtResult" variable
        stmtResult = linkCursor.fetchall()

        # if the number of fetched rows is greater than 0, which means that at least one product matches the search query
        if linkCursor.rowcount > 0:
            stmtResultDisplayed = ""
            for i in stmtResult:

                # the fetched results need to be "decoded" in order to be well displayed in a understandable language
                stmtResultRow = "- Product: " + i[0].decode() + "; description: " + i[1].decode(
                ) + "; remaining stock: " + str(i[2]) + "; unit price: " + str(round(i[3], 2)) + "€. \n"
                stmtResultDisplayed += stmtResultRow
        else:
            stmtResultDisplayed = "I am sorry, no product in our store has '" + \
                searchedProducts + "' in its name."

        dispatcher.utter_message(text=stmtResultDisplayed)

        # setting the "searchedProducts" slot to None after the answer makes it possible to search for another product in the same conversation
        return [SlotSet("searchedProducts", None)]

""" Fonction used to update the end-user's first name used in his eCommerce account """
class UpdateUserFirstName(Action):
    def name(self) -> Text:
        return "action_updateUserFirstName"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        linkCursor = link.cursor(prepared=True)
        stmt = "UPDATE UserEcommerce SET userFirstName = ? WHERE userId = ?"
        userFirstName = tracker.get_slot("userNewFirstName")
        customDataDict = extract_metadata_from_tracker(tracker)
        userId = customDataDict["session_userId"]
        linkCursor.execute(stmt, (userFirstName, userId, ))
        link.commit()

        utter_userFirstNameModified = "Your first name has been changed to {} in your account information!".format(
            userFirstName)
        dispatcher.utter_message(text=utter_userFirstNameModified)

        return [SlotSet("userNewFirstName", None)]


""" Fonction used to update the end-user's email adress used in his eCommerce account """
class UpdateUserEmailAdress(Action):
    def name(self) -> Text:
        return "action_updateUserEmailAdress"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        linkCursor = link.cursor(prepared=True)
        stmt = "UPDATE UserEcommerce SET userEmailAdress = ? WHERE userId = ?"
        userEmailAdress = tracker.get_slot("userNewEmailAdress")
        customDataDict = extract_metadata_from_tracker(tracker)
        userId = customDataDict["session_userId"]
        linkCursor.execute(stmt, (userEmailAdress, userId, ))
        link.commit()

        utter_userEmailAdressModified = "Your email adress has been correctly changed to {} in your account information!".format(
            userEmailAdress)
        dispatcher.utter_message(text=utter_userEmailAdressModified)

        return [SlotSet("userNewEmailAdress", None)]


""" Fonction used to insert into eCommerce's database a new product suggestion made by the end-user """
class InsertNewProductSuggestion(Action):
    def name(self) -> Text:
        return "action_insertNewProductSuggestion"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        linkCursor = link.cursor(prepared=True)
        stmt = "INSERT INTO SuggestionEcommerce (suggestionText) VALUES (?)"
        suggestionText = tracker.get_slot("suggestedProduct")
        linkCursor.execute(stmt, (suggestionText, ))
        link.commit()

        dispatcher.utter_message(text="Thanks for the suggestion!")

        return [SlotSet("suggestedProduct", None)]


""" Fonction used to insert into eCommerce's database an email adress related to the request so the customer service can reach the end-user directly afterwards """
class InsertNewMailForArequest(Action):
    def name(self) -> Text:
        return "action_insertNewMailForArequest"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        linkCursor = link.cursor(prepared=True)
        stmt = "INSERT INTO CustomRequestEcommerce (customRequestEmailAdress, customRequestText) VALUES (?, ?)"
        customRequestEmailAdress = tracker.get_slot("customRequestEmailAdress")
        customRequestText = ""
        linkCursor.execute(stmt, (customRequestEmailAdress, customRequestText, ))
        link.commit()
        customRequestId = linkCursor.lastrowid

        dispatcher.utter_message(
            text="Thank you for your contact information!")

        return [SlotSet("customRequestId", customRequestId)]


""" Fonction used to add the customer request's text made by the end-user """
class AddNewCustomRequest(Action):
    def name(self) -> Text:
        return "action_addNewCustomRequest"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        link = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="eCommerceDB")

        linkCursor = link.cursor(prepared=True)
        stmt = "UPDATE CustomRequestEcommerce SET customRequestText = ? WHERE customRequestId = ?"
        customRequestText = tracker.get_slot("customRequestText")
        customRequestId = tracker.get_slot("customRequestId")
        linkCursor.execute(stmt, (customRequestText, customRequestId, ))
        link.commit()

        customRequestEmailAdress = tracker.get_slot("customRequestEmailAdress")
        utter_customRequestMade = "Thank you for your request, it has been correctly forwarded to customer service! We will answer you directly on your mailbox {}".format(
            customRequestEmailAdress)
        dispatcher.utter_message(text=utter_customRequestMade)

        return [SlotSet("customRequestEmailAdress", None), SlotSet("customRequestId", None), SlotSet("customRequestText", None)]