import os
import flask
import flask_session
import pandas
import plotly.express
import sqlite3
import threading, webbrowser
import views
import text_data

# cursor.execute("""CREATE TABLE User_data (Username varchar(15), Name varchar(25), Password varchar(15));""")
# cursor.execute("""CREATE TABLE Personality_data (Username varchar(15), Datalist varchar(80), Name varchar(25));""")
app= flask.Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
flask_session.Session(app)

@app.route("/", methods= ["GET", "POST"])
def home():
    flask.session["username"]= ""
    return flask.render_template("login.html", error_message= "")

@app.route("/user_login", methods= ["GET", "POST"])
def user_login():
    data_dict= flask.request.form.to_dict()
    print("Login dict is :", data_dict)
    username= data_dict["username"]
    password= data_dict["password"]
    if (username == "Admin" and password == "abcd@1234"):
        connection= sqlite3.connect(os.path.join(os.getcwd(), "Database", "personality_database.db"))
        cursor= connection.cursor()
        cursor.execute(f"""SELECT * FROM Personality_data;""")
        userid_names= [(x[0], x[2]) for x in cursor.fetchall()]
        connection.close()
        return flask.render_template("admin_home.html", userid_names= userid_names)
        
    user_df= pandas.read_csv(filepath_or_buffer= os.path.join(os.getcwd(), "Database", "User data.csv"))
    user_data= [(user_df["Username"][i], user_df["Name"][i], user_df["Password"][i]) for i in range(0, len(user_df))]
    for element in user_data:
        if (username == element[0] and password == element[2]):
            flask.session["username"]= element[0]
            flask.session["name"]= element[1]
            break
    if flask.session["username"] == "":
        return flask.render_template("login.html", error_message= "Login credentials are incorrect. Please enter valid credentials.")
    else:
        return flask.render_template("home.html", name= flask.session["name"], big_five_traits_dict= text_data.big_five_traits_dict, traits_list= list(text_data.big_five_traits_dict.keys()))

@app.route("/save_responses/<string:responses>", methods= ["GET", "POST"])
def save_responses(responses):
    responses_list= [int(x) for x in responses.split(",")]
    username= flask.session["username"]
    name= flask.session["name"]
    trait_score_dict= views.save_trait_responses(username, responses_list, name)

    # Convert data into a DataFrame for Plotly
    df = pandas.DataFrame(list(trait_score_dict.items()), columns= ["Trait", "Score"])
    # Plot interactive bar chart
    fig = plotly.express.bar(data_frame= df, x= "Trait", y= "Score", title= "Bar plot", color= "Trait", 
                color_discrete_sequence= plotly.express.colors.qualitative.Set1)
    fig.update_layout(yaxis_range= [0, 100], xaxis_title= "Personality traits", yaxis_title= "Scores")
    # Generate the HTML for the plot
    plotly_graph= fig.to_html(full_html= False)
    
    candidate_feedback_dict= {}
    for trait in trait_score_dict.keys():
        if trait_score_dict[trait] < 50:
            candidate_feedback_dict[trait]= text_data.low_score_for_candidate[trait]
        elif trait_score_dict[trait] >= 50:
            candidate_feedback_dict[trait]= text_data.high_score_for_candidate[trait]
    return flask.render_template("dashboard.html", name= flask.session["name"], traits_list= list(text_data.big_five_traits_dict.keys()), trait_score_dict= trait_score_dict, candidate_feedback_dict= candidate_feedback_dict, plotly_graph= plotly_graph)

@app.route("/show_responses", methods= ["GET", "POST"])
def show_responses():
    candidate_username= flask.request.form.get("candidate_username")
    (candidate_name, trait_score_dict, other_candidates_trait_score_dict)= views.show_trait_responses(candidate_username)
    print(trait_score_dict, other_candidates_trait_score_dict, sep= "\n")
    
    # Convert data into a DataFrame for Plotly
    df = pandas.DataFrame(list(trait_score_dict.items()), columns= ["Trait", "Score"])
    # Plot interactive bar chart
    fig = plotly.express.bar(data_frame= df, x= "Trait", y= "Score", title= "Bar plot for comparing Candidate's score vs others' average scores", color= "Trait", 
                color_discrete_sequence= plotly.express.colors.qualitative.Set1)
    fig.add_bar(x= list(other_candidates_trait_score_dict.keys()), y= list(other_candidates_trait_score_dict.values()), name= "Other candidates average")
    fig.update_layout(yaxis_range= [0, 100], xaxis_title= "Personality traits", yaxis_title= "Scores")
    # Generate the HTML for the plot
    plotly_graph= fig.to_html(full_html= False)
    
    candidate_feedback_dict= {}
    for trait in trait_score_dict.keys():
        if trait_score_dict[trait] <= 32:
            candidate_feedback_dict[trait]= text_data.low_score_for_hr[trait]
        elif 68 >= trait_score_dict[trait] > 32:
            candidate_feedback_dict[trait]= text_data.average_score_for_hr[trait]
        elif trait_score_dict[trait] > 68:
            candidate_feedback_dict[trait]= text_data.high_score_for_hr[trait]
    return flask.render_template("admin_dashboard.html", candidate_name= candidate_name, traits_list= list(trait_score_dict.keys()), trait_score_dict= trait_score_dict, other_candidates_trait_score_dict= other_candidates_trait_score_dict, candidate_feedback_dict= candidate_feedback_dict, plotly_graph= plotly_graph)
    
if __name__ == "__main__":
    port= 5000
    url= "http://127.0.0.1:{0}/".format(port)
    threading.Timer(1.05, lambda: webbrowser.open(url)).start()
    app.run(port= port, debug= True, use_reloader= False, threaded= True)



