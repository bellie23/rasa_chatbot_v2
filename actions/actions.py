import re
import random
import pandas as pd
from typing import Any, Text, Dict, List
from rasa_sdk.events import SlotSet, Restarted
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

"""
Movie Booking Chatbot Action Server Module

This module implements a RASA action server for a movie booking chatbot system.
It handles movie information display, theater selection, and booking processes.
The system uses a CSV file containing IMDB movie data and manages theater/showtime information.
"""

df = pd.read_csv("/home/koursthan/workspace/rasa_chatbot_v2/data/imdb_top_1000.csv")
available_movies = random.sample(df["Series_Title"].to_list(), 5)

AVAILABLE_THEATERS = ["Pillage at the Mall", "Pillage Renti", "Pillage Agios Dimitrios"]
AVAILABLE_SHOWTIMES = ["2:30 PM", "5:00 PM", "7:15 PM", "9:30 PM", "10:20 PM", "11:45 PM"]
AVAILABLE_ROOMS = {
    "Regular": 7,
    "Dolby Atmos": 12,
    "VMAX Sphera": 15
}

movie_payloads = {}

for movie in available_movies:
    room, price = random.choice(list(AVAILABLE_ROOMS.items()))

    movie_payloads[movie] = {
        "theaters": random.sample(AVAILABLE_THEATERS, 2),
        "showtimes": random.sample(AVAILABLE_SHOWTIMES, 3),
        "room": room,
        "price": price,
        "available_seats": random.randint(0, 250)
    }


class DisplayAvailableMovies(Action):
    """
    RASA action to display the list of currently available movies.
    
    This action retrieves the randomly selected movies from the global available_movies
    list and presents them to the user in a formatted list.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_display_available_movies"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of displaying available movies.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            An empty list of events
        """
        dispatcher.utter_message(text="Tonight's movies are:\n- " + '\n- '.join(available_movies))
        return []


class DisplayMovieInfo(Action):
    """
    RASA action to display detailed information about a specific movie.
    
    Retrieves and displays comprehensive movie information including release year,
    runtime, genre, director, rating, star, and overview from the IMDB dataset.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_display_movie_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of displaying detailed movie information.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            A list containing a SlotSet event to clear the movie slot
        """
        selected_movie = tracker.get_slot("movie")

        if selected_movie in available_movies:
            info = df[df["Series_Title"] == selected_movie].to_dict()

            title = list(info["Series_Title"].values())[0]
            release_year = list(info["Released_Year"].values())[0]
            runtime = list(info["Runtime"].values())[0]
            genre = list(info["Genre"].values())[0]
            director = list(info["Director"].values())[0]
            rating = list(info["IMDB_Rating"].values())[0]
            star = list(info["Star1"].values())[0]
            overview = list(info["Overview"].values())[0]

            message = f"""Here is some info on {title}: 

- Year: {release_year}
- Runtime: {runtime}
- Genre: {genre}
- Director: {director}
- Rating: {rating}
- Star: {star}
- Overview: {overview}
"""
        else:
            message = f"I'm sorry, but I don't have any info available on {selected_movie}"

        dispatcher.utter_message(message)
        return [SlotSet("movie", None)]


class ActionAskBookMovie(Action):
    """
    RASA action to initiate the movie booking process by asking the user to select a movie.
    
    Displays the list of available movies for the user to choose from.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_ask_book_movie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of requesting movie selection from the user.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            An empty list of events
        """
        dispatcher.utter_message(text="Please select a film. Tonight's movies are:\n- " + '\n- '.join(available_movies))
        return []


class ActionAskBookTheater(Action):
    """
    RASA action to handle theater selection in the booking process.
    
    Presents available theaters for the selected movie and handles invalid selections
    by restarting the booking process if necessary.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_ask_book_theater"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of requesting theater selection from the user.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            A list of events, either empty for success or reset events for failure
        """
        movie = tracker.get_slot("book_movie")

        try:
            dispatcher.utter_message(text="Please select a theater:\n- " + '\n- '.join(movie_payloads[movie]["theaters"]))
            return []

        except Exception as e:
            dispatcher.utter_message(text="Invalid Request. Please restart the booking process")
            return [
                SlotSet("book_movie", None),
                SlotSet("book_theater", None),
                SlotSet("book_time", None),
                SlotSet("num_tickets", None),
                SlotSet("e_mail", None),
                Restarted()
            ]


class ActionAskBookTime(Action):
    """
    RASA action to handle showtime selection in the booking process.
    
    Presents available showtimes for the selected movie and theater combination,
    handles invalid selections by restarting the booking process if necessary.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_ask_book_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of requesting showtime selection from the user.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            A list of events, either empty for success or reset events for failure
        """
        movie = tracker.get_slot("book_movie")
        theater = tracker.get_slot("book_theater")

        try:
            if theater in movie_payloads[movie]["theaters"]:
                dispatcher.utter_message(text="Please select a booking time:\n- " + '\n- '.join(movie_payloads[movie]["showtimes"]))
                return []

            else:
                dispatcher.utter_message(text="Invalid Theater. Please restart the booking process")
                return [
                    SlotSet("book_movie", None),
                    SlotSet("book_theater", None),
                    SlotSet("book_time", None),
                    SlotSet("num_tickets", None),
                    SlotSet("e_mail", None),
                    Restarted()
                ]

        except Exception as e:
            dispatcher.utter_message(text="Invalid Request. Please restart the booking process")
            return [
                SlotSet("book_movie", None),
                SlotSet("book_theater", None),
                SlotSet("book_time", None),
                SlotSet("num_tickets", None),
                SlotSet("e_mail", None),
                Restarted()
            ]


class ActionAskNumTickets(Action):
    """
    RASA action to handle ticket quantity selection in the booking process.
    
    Displays room type, ticket price, and available seats information,
    then prompts the user to specify the number of tickets they want to purchase.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_ask_num_tickets"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of requesting the number of tickets from the user.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            A list of events, either empty for success or reset events for failure
        """
        movie = tracker.get_slot("book_movie")

        room = movie_payloads[movie]["room"]
        price = movie_payloads[movie]["price"]
        available_seats = movie_payloads[movie]["available_seats"]
        time = tracker.get_slot("book_time")

        try:
            if time in movie_payloads[movie]["showtimes"]:
                dispatcher.utter_message(text="The movie is playing at the " + room + f" showroom. The price of admission is {price} Euros. Currently there are {available_seats} tickets available. How many tickets would you like?")
                return []
            else:
                dispatcher.utter_message(text="Invalid Booking Time. Please restart the booking process")
                return [
                    SlotSet("book_movie", None),
                    SlotSet("book_theater", None),
                    SlotSet("book_time", None),
                    SlotSet("num_tickets", None),
                    SlotSet("e_mail", None),
                    Restarted()
                ]

        except Exception as e:
            dispatcher.utter_message(text="Invalid Request. Please restart the booking process")
            return [
                SlotSet("book_movie", None),
                SlotSet("book_theater", None),
                SlotSet("book_time", None),
                SlotSet("num_tickets", None),
                SlotSet("e_mail", None),
                Restarted()
            ]


class ActionAskEmail(Action):
    """
    RASA action to handle email collection in the booking process.
    
    Verifies ticket availability based on requested quantity and prompts
    for email address if seats are available.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_ask_e_mail"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of requesting the user's email address.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            A list of events, either empty for success or reset events for failure
        """
        movie = tracker.get_slot("book_movie")
        num_tickets = tracker.get_slot("num_tickets")

        try:
            if int(num_tickets) < movie_payloads[movie]["available_seats"]:
                dispatcher.utter_message(text="Please submit your e-mail address.")

            else:
                dispatcher.utter_message(text="Not enough seats available. Restarting the process.")
                return [
                    SlotSet("book_movie", None),
                    SlotSet("book_theater", None),
                    SlotSet("book_time", None),
                    SlotSet("num_tickets", None),
                    SlotSet("e_mail", None),
                    Restarted()
                ]

        except Exception as e:
            dispatcher.utter_message(text="Invalid Request. Please restart the booking process")
            return [
                SlotSet("book_movie", None),
                SlotSet("book_theater", None),
                SlotSet("book_time", None),
                SlotSet("num_tickets", None),
                SlotSet("e_mail", None),
                Restarted()
            ]


class ActionReturnSummary(Action):
    """
    RASA action to display the final booking summary.
    
    Validates the email address format and displays a complete summary of the booking
    including movie, theater, time, number of tickets, total price, and email.
    Resets all slots after displaying the summary.
    """

    def name(self) -> Text:
        """Returns the name of the action."""
        return "action_return_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Executes the action of displaying the booking summary.
        
        Args:
            dispatcher: The dispatcher which is used to send messages back to the user
            tracker: The state tracker for the current user conversation
            domain: The bot's domain configuration
            
        Returns:
            A list of events to reset all slots and restart the conversation
        """
        e_mail = tracker.get_slot("e_mail")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", e_mail):
            dispatcher.utter_message("Invalid e-mail address. Restarting the Process.")

        else:
            message = f"""----Booking Summary----
    - Film: {tracker.get_slot("book_movie")}
    - Theater: {tracker.get_slot("book_theater")}
    - Time: {tracker.get_slot("book_time")}
    - Total tickets: {tracker.get_slot("num_tickets")}
    - Price: {price * int(tracker.get_slot("num_tickets"))}
    - E-mail: {e_mail}
    """
            dispatcher.utter_message(message)

        return [
            SlotSet("book_movie", None),
            SlotSet("book_theater", None),
            SlotSet("book_time", None),
            SlotSet("num_tickets", None),
            SlotSet("e_mail", None),
            Restarted()
        ]