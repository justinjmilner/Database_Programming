import psycopg2
from psycopg2 import OperationalError, errors
from decimal import Decimal
import datetime
from collections import defaultdict

def member_activity_dashboard(connection):
    cursor = connection.cursor()
    entity_email = input("Enter the member's email to view the dashboard: ")
    try:
        # Fetch donation activities
        cursor.execute("""
            SELECT campaign_issue, campaign_location, donation_date, amount
            FROM Donations
            WHERE entity_email = %s;
        """, (entity_email,))
        donations = cursor.fetchall()
        
        # Fetch volunteering activities
        cursor.execute("""
            SELECT campaign_issue, campaign_location, campaign_start_date, involvement_start_date, involvement_end_date
            FROM MembershipHistory
            WHERE entity_email = %s;
        """, (entity_email,))
        volunteering = cursor.fetchall()

        # Fetch scheduled activities
        cursor.execute("""
            SELECT campaign_issue, campaign_location, campaign_start_date, scheduled_date
            FROM Scheduled
            WHERE entity_email = %s;
        """, (entity_email,))
        scheduled = cursor.fetchall()

        # Compile the dashboard
        print(f"Activity Dashboard for {entity_email}:")
        print("Donations:")
        for donation in donations:
            print(f"Issue: {donation[0]}, Location: {donation[1]}, Date: {donation[2]}, Amount: {donation[3]}")

        print("\nVolunteering:")
        for volunteer in volunteering:
            print(f"Issue: {volunteer[0]}, Location: {volunteer[1]}, Campaign Start: {volunteer[2]}, Involvement: {volunteer[3]} to {volunteer[4]}")

        print("\nScheduled Activities:")
        for schedule in scheduled:
            print(f"Issue: {schedule[0]}, Location: {schedule[1]}, Campaign Start: {schedule[2]}, Scheduled Date: {schedule[3]}")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def calculate_engagement_score(connection):
    cursor = connection.cursor()
    engagement_scores = defaultdict(int)

    try:
        # Define the scoring criteria
        scores = {
            'donation': 10,  # points per donation transaction
            'volunteering': 20,  # points per volunteering event
            # Add other criteria as needed
        }
        
        # Fetch members' donation activities and calculate scores
        cursor.execute("""
            SELECT entity_email, COUNT(*) * %s AS donation_score
            FROM Donations
            GROUP BY entity_email
        """, (scores['donation'],))
        donation_scores = cursor.fetchall()
        for email, score in donation_scores:
            engagement_scores[email] += score

        # Fetch members' volunteering activities and calculate scores
        cursor.execute("""
            SELECT entity_email, COUNT(*) * %s AS volunteering_score
            FROM MembershipHistory
            WHERE involvement_end_date IS NULL OR involvement_end_date > CURRENT_DATE
            GROUP BY entity_email
        """, (scores['volunteering'],))
        volunteering_scores = cursor.fetchall()
        for email, score in volunteering_scores:
            engagement_scores[email] += score

        # Print the engagement scores
        for email, total_score in engagement_scores.items():
            print(f"Member Email: {email}, Engagement Score: {total_score}")


    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()


def update_membership_history_annotation(connection):
    # Gather all necessary information
    entity_email = input("Enter entity email: ")
    campaign_issue = input("Enter campaign issue: ")
    campaign_location = input("Enter campaign location: ")
    campaign_start_date = input("Enter campaign start date (YYYY-MM-DD): ")
    new_annotation = input("Enter new annotation: ")
    
    cursor = connection.cursor()
    try:
        # Prepare the update query with placeholders for each parameter
        update_query = """
        UPDATE MembershipHistory
        SET annotations = %s
        WHERE entity_email = %s AND campaign_issue = %s AND campaign_location = %s AND campaign_start_date = %s;
        """
        
        # Execute the update query with the provided values
        cursor.execute(update_query, (new_annotation, entity_email, campaign_issue, campaign_location, campaign_start_date))
        
        # Commit the changes to the database
        connection.commit()
        
        if cursor.rowcount == 0:
            print("No matching membership history found or no changes were made.")
        else:
            print("Membership history annotation updated successfully for the specific campaign.")
            
    except psycopg2.Error as e:
        # Rollback the transaction if any error occurs
        connection.rollback()
        print(f"An error occurred while updating the annotation: {e}")
    finally:
        # Close the cursor
        cursor.close()

def add_membership_history(connection):
    entity_email = input("Enter entity email: ")
    campaign_issue = input("Enter campaign issue: ")
    campaign_location = input("Enter campaign location: ")
    campaign_start_date = input("Enter campaign start date (YYYY-MM-DD): ")
    involvement_start_date = input("Enter involvement start date (YYYY-MM-DD): ")
    involvement_end_date = input("Enter involvement end date (YYYY-MM-DD): ")
    annotations = input("Enter annotations: ")
    cursor = connection.cursor()
    try:
        # Prepare the insert query with placeholders
        insert_query = """
        INSERT INTO MembershipHistory (
            entity_email,
            campaign_issue,
            campaign_location,
            campaign_start_date,
            involvement_start_date,
            involvement_end_date,
            annotations
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        # Execute the insert query with the provided values
        cursor.execute(insert_query, (
            entity_email,
            campaign_issue,
            campaign_location,
            campaign_start_date,
            involvement_start_date,
            involvement_end_date,
            annotations
        ))
        
        # Commit the changes to the database
        connection.commit()
        
        print("Membership history added successfully.")
    except psycopg2.Error as e:
        # Rollback the transaction if any error occurs
        connection.rollback()
        print(f"An error occurred while adding membership history: {e}")
    finally:
        # Close the cursor
        cursor.close()


def add_campaign_annotation(connection):
    issue = input("Enter issue: ")
    location = input("Enter location: ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    annotation = input("Enter annotation: ")
    cursor = connection.cursor()
    try:
        # Prepare the update query with placeholders
        update_query = """
        UPDATE Campaigns
        SET annotations = %s
        WHERE issue = %s AND location = %s AND start_date = %s;
        """
        
        # Execute the update query with the provided values
        cursor.execute(update_query, (annotation, issue, location, start_date))
        
        # Commit the changes to the database
        connection.commit()
        
        print("Annotation added to campaign successfully.")
    except psycopg2.Error as e:
        # Rollback the transaction if any error occurs
        connection.rollback()
        print(f"An error occurred while adding annotation: {e}")
    finally:
        # Close the cursor
        cursor.close()


def register_donor(connection):
    cursor = connection.cursor()
    try:
        # Get donor information
        donor_email = input("Enter donor email: ")
        donor_name = input("Enter donor name: ")
        
        # Check if the donor already exists
        cursor.execute("SELECT * FROM Entity WHERE email = %s;", (donor_email,))
        if cursor.fetchone() is not None:
            print("A donor with this email already exists.")
            return

        # Insert new donor
        insert_query = "INSERT INTO Entity (Email, Name) VALUES (%s, %s);"
        cursor.execute(insert_query, (donor_email, donor_name))
        
        connection.commit()
        print("New donor added successfully.")
    except OperationalError as e:
        connection.rollback()
        print(f"The error '{e}' occurred")
    except psycopg2.Error as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def make_donation(connection):
    cursor = connection.cursor()
    try:
        # Get donor information
        donor_email = input("Enter donor email: ")
        cursor.execute("SELECT * FROM Entity WHERE email = %s;", (donor_email,))
        if cursor.fetchone() is None:
            print("No donor found with the given email. Please add the donor first.")
            return
        
        # Get campaign information
        campaign_issue = input("Enter campaign issue: ")
        campaign_location = input("Enter campaign location: ")
        campaign_start_date = input("Enter campaign start date (YYYY-MM-DD): ")
        cursor.execute("SELECT * FROM Campaigns WHERE issue = %s AND location = %s AND start_date = %s;",
                       (campaign_issue, campaign_location, campaign_start_date))
        if cursor.fetchone() is None:
            print("No campaign found with the given details. Please add the campaign first.")
            return
        
        # Get donation details
        donation_date = input("Enter donation date (YYYY-MM-DD): ")
        amount = input("Enter donation amount: ")

        # Insert donation
        insert_query = """
        INSERT INTO Donations (entity_email, campaign_issue, campaign_location, campaign_start_date, donation_date, amount)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (donor_email, campaign_issue, campaign_location, campaign_start_date, donation_date, amount))
        
        connection.commit()
        print("Donation added successfully.")
    except OperationalError as e:
        connection.rollback()
        print(f"The error '{e}' occurred")
    except psycopg2.Error as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def print_accounting_report(connection):
    cursor = connection.cursor()
    try:
        # Query to get the total donations per campaign
        cursor.execute("""
            SELECT c.issue, c.budget, COALESCE(SUM(d.amount), 0) as total_donations
            FROM Campaigns c
            LEFT JOIN Donations d ON c.issue = d.campaign_issue AND c.location = d.campaign_location AND c.start_date = d.campaign_start_date
            GROUP BY c.issue, c.budget
            ORDER BY c.issue;
        """)
        results = cursor.fetchall()

        if not results:
            print("No campaigns found.")
            return

        print("Budget Coverage by Donations:")
        for issue, budget, total_donations in results:
            if budget > 0:  # Avoid division by zero
                coverage_percentage = (total_donations / budget) * 100
                bar_length = int(coverage_percentage / 2)  # Here, 100% = 50 characters in bar length
                bar_chart = '#' * bar_length
                print(f"Campaign: {issue}, Budget: {budget}, Donations: {total_donations}, Coverage: {coverage_percentage:.2f}%")
                print(f"[{bar_chart}]")
            else:
                print(f"Campaign: {issue}, Budget: {budget}, Donations: {total_donations}, Coverage: N/A (No budget specified)")

    except OperationalError as e:
        print(f"The error '{e}' occurred")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()

def add_volunteer(connection):
    cursor = connection.cursor()
    try:
        email = input("Enter volunteer email: ")
        name = input("Enter name: ")
        tier = input("Enter tier: ")
        issue = input("Enter issue: ")
        location = input("Enter location: ")
        start_date = input("Enter campaign start date (YYYY-MM-DD): ")
        volunteer_start_date = input("Enter volunteer start date (YYYY-MM-DD): ")

        # Use parameterized queries to prevent SQL injection
        cursor.execute("INSERT INTO Entity (Email, Name) VALUES (%s, %s);", (email, name))
        cursor.execute("INSERT INTO Volunteer (entity_email, Tier) VALUES (%s, %s);", (email, tier))
        cursor.execute("INSERT INTO Scheduled (Entity_Email, Campaign_Issue, Campaign_Location, Campaign_Start_Date, Scheduled_Date) VALUES (%s, %s, %s, %s, %s);", (email, issue, location, start_date, volunteer_start_date))
        
        connection.commit()
        print("Volunteer added successfully.")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    except psycopg2.errors.UniqueViolation as e:
        print("This email is already used for a volunteer.")
        connection.rollback()
    except psycopg2.errors.ForeignKeyViolation as e:
        print("The campaign details provided do not match any existing campaigns.")
        connection.rollback()
    finally:
        cursor.close()

def schedule_volunteer(connection):
    cursor = connection.cursor()
    try:
        email = input("Enter volunteer email: ")
        issue = input("Enter issue: ")
        location = input("Enter location: ")
        start_date = input("Enter campaign start date (YYYY-MM-DD): ")
        volunteer_start_date = input("Enter volunteer start date (YYYY-MM-DD): ")

        insert_query = """INSERT INTO Scheduled (Entity_Email, Campaign_Issue, Campaign_Location, Campaign_Start_Date, Scheduled_Date) VALUES (%s, %s, %s, %s, %s);"""
        cursor.execute(insert_query, (email, issue, location, start_date, volunteer_start_date))
        
        connection.commit()
        print("Volunteer scheduled successfully.")
    except OperationalError as e:
        connection.rollback()  # Rollback the transaction on error
        print(f"The error '{e}' occurred")
    except psycopg2.Error as e:  # Catch any other database related errors
        connection.rollback()  # Rollback the transaction on error
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def create_campaign(connection):
    cursor = connection.cursor()
    try:
        issue = input("Enter issue: ")
        location = input("Enter location: ")
        start_date = input("Enter start date (YYYY-MM-DD): ")
        duration_days = input("Enter duration days: ")
        phase = input("Enter phase: ")
        budget = input("Enter budget: ")
        website_push_date = input("Enter website push date (YYYY-MM-DD): ")

        # Use parameterized queries to safely insert data
        campaign_insert_query = """
        INSERT INTO Campaigns (Issue, Location, Start_Date, Duration_Days, Phase, Budget, Website_Push_Date)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        campaign_values = (issue, location, start_date, duration_days, phase, budget, website_push_date)
        cursor.execute(campaign_insert_query, campaign_values)
        
        connection.commit()
        print("Campaign created successfully.")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    except errors.UniqueViolation as e:
        print("This campaign already exists.")
        connection.rollback()
    except errors.ForeignKeyViolation as e:
        print("One or more foreign key constraints failed.")
        connection.rollback()
    except errors.CheckViolation as e:
        print("One or more checks failed.")
        connection.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()

def view_campaign_status(connection):
    cursor = connection.cursor()
    try:
        issue = input("Enter issue: ")
        location = input("Enter location: ")
        start_date = input("Enter start date (YYYY-MM-DD): ")

        # Use parameterized queries to safely insert data
        select_query = """
        SELECT * FROM Campaigns 
        WHERE issue = %s AND location = %s AND start_date = %s;
        """
        cursor.execute(select_query, (issue, location, start_date))
        results = cursor.fetchall()
        
        if not results:
            print("No campaign found with the provided details.")
        else:
            for row in results:
                formatted_row = [str(item) if isinstance(item, (datetime.date, Decimal)) else item for item in row]
                print(formatted_row)

    except OperationalError as e:
        print(f"The error '{e}' occurred")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()


def create_connection(db_name, db_user, db_password, db_host):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # Fetch all rows from the last executed query
        result = cursor.fetchall()
        for row in result:
            # Convert datetime and Decimal objects to strings
            formatted_row = [str(item) if isinstance(item, (datetime.date, Decimal)) else item for item in row]
            print(formatted_row)
        # Make sure to close the cursor after execution
        cursor.close()
    except OperationalError as e:
        print(f"The error '{e}' occurred")

def main():
    db_name = 'c370_s097'
    db_user = 'c370_s097'
    db_password = 'oncTGYfw'
    db_host = 'studentdb.csc.uvic.ca'

    connection = create_connection(
        db_name, db_user, db_password, db_host
    )

    # If connection was successful, do something with it here
    if connection is not None:
        try:
            while True:
                print("\nPlease select a query to execute:")
                print("1. List all entities who have made a donation")
                print("2. List total donations from each entity")
                print("3. List campaigns with donations exceeding 1000$")
                print("4. List entities who are both a member and employee")
                print("5. List campaigns with no donations")
                print("6. List entities scheduled for campaigns after June 1, 2023")
                print("7. List all entities with their roles")
                print("8. List the highest donation for each campaign")
                print("9. List campaigns with more than one donation")
                print("10. List total days for each campaign")
                print("11. Schedule an event")
                print("12. Add a new volunteer")
                print("13. Schedule a volunteer")
                print("14. View the status of a campaign")
                print("15. Print accounting report")
                print("16. Make a donation")
                print("17. Register a new donor")
                print("18. Add an annotation to a campaign")
                print("19. Add membership history")
                print("20. Update membership history annotation")
                print("21. Calculate engagement score")
                print("22. Member activity dashboard")
                print("0. Exit")
                choice = input("Enter your choice: ")

                if choice == "1":
                    execute_query(connection, "select e.email, e.name from Entity e where exists (select d.entity_email from donations d where e.email = d.entity_email);")
                elif choice == "2":
                    execute_query(connection, "select d.entity_email, SUM(d.amount) as total_donations from donations d group by d.entity_email;")
                elif choice == "3":
                    execute_query(connection, "select c.* from Campaigns c where c.issue in (select d.campaign_issue from Donations d group by d.campaign_issue having SUM(d.amount) > 1000);")
                elif choice == "4":
                    execute_query(connection, "select entity_email from Member intersect select entity_email from Employee;")
                elif choice == "5":
                    execute_query(connection, "select * from Campaigns c where not exists (select 1 from Donations d where d.campaign_issue = c.issue and d.campaign_location = c.location and d.campaign_start_date = c.start_date);")
                elif choice == "6":
                    execute_query(connection, "select distinct s.entity_email from Scheduled s where s.campaign_start_date >= '2023-06-01';")
                elif choice == "7":
                    execute_query(connection, "select e.email, e.name, 'Volunteer' as role from entity e join volunteer v on e.email = v.entity_email union select e.email, e.name, 'Member' as role from entity e join member m on e.email = m.entity_email union select e.email, e.name, 'Employee' as role from entity e join employee p on e.email = p.entity_email;")
                elif choice == "8":
                    execute_query(connection, "select campaign_issue, MAX(amount) as highest_donation from donations group by campaign_issue;")
                elif choice == "9":
                    execute_query(connection, "select campaign_issue, count(*) as donation_counts from donations group by campaign_issue having count (*) > 1;")
                elif choice == "10":
                    execute_query(connection, "select issue, SUM(duration_days) as total_days from campaigns group by issue;")
                elif choice == "11":
                    create_campaign(connection)
                elif choice == "12":
                    add_volunteer(connection)
                elif choice == "13":
                    schedule_volunteer(connection)
                elif choice == "14":
                    view_campaign_status(connection)
                elif choice == "15":
                    print_accounting_report(connection)
                elif choice == "16":
                    make_donation(connection)
                elif choice == "17":
                    register_donor(connection)
                elif choice == "18":
                    add_campaign_annotation(connection)
                elif choice == "19":
                    add_membership_history(connection)
                elif choice == "20":
                    update_membership_history_annotation(connection)
                elif choice == "21":
                    calculate_engagement_score(connection)
                elif choice == "22":
                    member_activity_dashboard(connection)
                elif choice == "0":
                    break
                else:   
                    print("Invalid choice. Please try again.")
        finally:
            try:
                connection.close()
                print("Database connection closed.")
            except:
                print("Closing connection error occurred")

        

if __name__ == "__main__":
    main()