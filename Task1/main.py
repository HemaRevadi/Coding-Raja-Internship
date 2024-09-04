from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import mysql.connector
from typing import Optional

app = FastAPI()

# Database connection
def create_connection():
    return mysql.connector.connect(
        host="localhost",        # Replace with your database host
        user="hema",     # Replace with your database username
        password="hema", # Replace with your database password
        database="amehchatbot"  # Replace with your database name
    )

# Function to book tickets
def book_ticket(tickets_booked: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = "INSERT INTO tickets (tickets_booked, booking_status) VALUES (%s, 'booked')"
        cursor.execute(query, (tickets_booked,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to cancel the most recently booked tickets
def cancel_recent_ticket():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Find the most recent booking that is still active
        query = """
        SELECT id FROM tickets
        WHERE booking_status = 'booked'
        ORDER BY booking_time DESC
        LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            ticket_id = result[0]
            # Update the booking status to 'canceled' for the most recent booking
            update_query = "UPDATE tickets SET booking_status = 'canceled' WHERE id = %s"
            cursor.execute(update_query, (ticket_id,))
            conn.commit()
        else:
            raise HTTPException(status_code=404, detail="No active bookings found to cancel.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Pydantic model for Dialogflow request
class DialogflowRequest(BaseModel):
    queryResult: dict
    session: Optional[str] = None

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: DialogflowRequest):
    intent = request.queryResult.get('intent').get('displayName')
    
    if intent == 'book.get':
        tickets = request.queryResult.get('parameters').get('number')
        if tickets:
            try:
                tickets = int(tickets)
                # Book the tickets in the database
                book_ticket(tickets)
                
                # Create a response
                response_text = f"Your {tickets} ticket(s) have been successfully booked!"
                return {
                    "fulfillmentText": response_text
                }
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid number of tickets.")
    
    elif intent == 'cancel-ticket':
        # Cancel the most recent booking
        try:
            cancel_recent_ticket()
            # Create a response
            response_text = "Your booking has been successfully canceled."
            return {
                "fulfillmentText": response_text
            }
        except HTTPException as http_exc:
            return {
                "fulfillmentText": str(http_exc.detail)
            }

    return {
        "fulfillmentText": "I didn't understand that. Could you please try again?"
    }

# To run the server, use: uvicorn main:app --reload
