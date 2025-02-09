# Cinema Assistant Chatbot

This is a Prototype Task-oriented Dialog System powered by the Rasa framework.

## Introduction

Welcome to **Pillage Cinemas**! Along with a whole suite of blockbusters for all tastes and ages, we offer a cutting-edge virtual assistant, eager to help our customers. The movie industry, apart from being one of the most well-documented through databases like IMDb, is also prime for hosting a number of online functionalities leveraging the power of chatbots and AI agents. The scope of this Virtual assistant encompasses 3 basic tasks:

- Online ticket booking
- On-the-fly information about available screenings
- Information regarding cancellation policies

## Data

In order to keep our virtual assistant knowledgeable and up to date, we utilize an external dataset, specifically the `IMDb Top 1000`. This is a comprehensive database extra that contains information about the top rated IMDB films. Each movie is accompanied by its corresponding metadata:

- Title
- Director
- Starring Actors
- Release Year
- Genre

And much much more... We also generate some synthetic data in order to simulate information regarding our movie theaters. If you take a look at `actions.py`, you will see that 5 films are sampled from the dataset at the initialization of the dialogue, in order to provide the films available for today's screenings. Each movie is accompanied by metadata related to:

- `theaters`: The theaters that provide the film
- `showtimes`: The times of the screenings
- `room`: The room of the screenings
- `price`: The price of admission related to the room
- `available_seats`: The number of the available seats within a room

## How to Run

```
pip install -r requirements.txt
rasa train
rasa shell
```

## Scenarios

The three main dialog flows supported by the virtual agent are:

- Checking available films
- Booking a ticket
- Cancelling a ticket

Let's see some examples:

### Check Available Films

```
- **User**: Hello
- **Bot**: Welcome to the Pillage Cinemas Virtual Assistant! How can I help you?
- **User**: What should I watch?
- **Bot**: Tonight's movies are:
    - Shutter Island
    - Giant
    - Rebel Without a Cause
    - Joker
    - La haine
- **User**: Do you have any info?
- **Bot**: Sure! What film would you like to know about?
- **User**: Joker
- **Bot**: Here is some info on Joker: 
    - Year: 2019
    - Runtime: 122 min
    - Genre: Crime, Drama, Thriller
    - Director: Todd Phillips
    - Rating: 8.5
    - Star: Joaquin Phoenix
    - Overview: In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime. This path brings him face-to-face with his alter-ego: the Joker.
```

The agent pulls out the database in order to fetch today's films at the beginning of the dialog flow. That helps maintain the consistency throughout all interactions until the bot is shut down.

### Booking Tickets

```
- **User**: Book ticket
- **Bot**: Please select a film. Tonight's movies are:
    - Shutter Island
    - Giant
    - Rebel Without a Cause
    - Joker
    - La haine
- **User**: Giant
- **Bot**: Please select a theater:
    - Pillage at the Mall
    - Pillage Renti
- **User**: Pillage Renti
- **Bot**: Please select a booking time:
    - 9:30 PM
    - 2:30 PM
    - 5:00 PM
- **User**: 5:00 PM
- **Bot**: The movie is playing at the Dolby Atmos showroom. The price of admission is 12 Euros. Currently there are 217 tickets available. How many tickets would you like?
- **User**: 2
- **Bot**: Please submit your e-mail address.
- **User**: ellie.beka@gmail.com
- **Bot**: ----Booking Summary----
    - Film: Giant
    - Theater: Pillage Renti
    - Time: 5:00 PM
    - Total tickets: 2
    - Price: 14
    - E-mail: ellie.beka@gmail.com
```

Note that every dialog step acts as a validation step to the previous step. For example, if the user selects a movie that is not available for screening, there is a fallback mechanism that restarts the process:

```
Invalid Request. Please restart the booking process
```

The user should trigger the dialog flow again by typing `book ticket` or another similar phrase (see `nlu.yml`).

### Cancelling Tickets

```
- **User**: cancel tickets
- **Bot**: I'm afraid cancellations cannot be made online. However, there are several cancellation options provided you speak to one of our employees in one of our theaters. Would you like to know more?
- **User**: You can cancel your tickets and either:
    - Get a full refund
    - Get a coupon for buying new tickets
    - Get credits for the arcade and our official Pillage Cinemas Movie Store
Can I help you with anything else?
```

## Challenges

- Making the dialog flow adaptive, such that it extracts information from the user's lines and uses it to make database calls. For this, rasa provides `slots` and `forms`
- Finding a smart way to interrupt the dialog flow when wrong information is provided by the user. For example in the booking process, when wrong information is entered, the dialog is restarted and the `slots` are all nullified

## Next Steps

- Integrate a real world database
- Use entity extraction (e.g. NER) to parse natural language questions, such as "Who directed Seven Samurai?"
- Implement more adaptive fallback mechanisms
- Provide more robust data validation schemes
- Support for multiple languages
- Use more modern frameworks and models (LLM-based)

## Contact 

- Name: Elissavet Beka
- S.N: lt12100022

## Presentation
https://docs.google.com/presentation/d/1oiStLW45hcaVm4gArXuG1KtVwB3za8PUalTEmHr6vrs/edit?usp=sharing