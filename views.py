import ast
import matplotlib.pyplot as plt
import numpy
import sqlite3
import os
import text_data

def save_trait_responses(username, responses_list, name):
    connection= sqlite3.connect(os.path.join(os.getcwd(), "Database", "personality_database.db"))
    cursor= connection.cursor()
    cursor.execute(f"""SELECT Datalist FROM Personality_data WHERE Username = {'"' + username + '"'};""")
    datalist= cursor.fetchall()
    if datalist == []:
        insert_query= """INSERT INTO Personality_data (Username, Datalist, Name) VALUES(?, ?, ?)"""
        data_tuple= (username, str(responses_list), name)
        cursor.execute(insert_query, data_tuple)
    else:
        cursor.execute(f"""UPDATE Personality_data SET Datalist = {'"' + str(responses_list) + '"'}, Name = {'"' + name + '"'} WHERE Username = {'"' + username + '"'};""")
    connection.commit()
    connection.close()
    
    trait_score_dict= {trait: 0 for trait in text_data.big_five_traits_dict.keys()}
    trait_score_dict["Openness"]= sum(responses_list[0: 5]) * 4
    trait_score_dict["Conscientiousness"]= sum(responses_list[5: 10]) * 4
    trait_score_dict["Extraversion"]= sum(responses_list[10: 15]) * 4
    trait_score_dict["Agreeableness"]= sum(responses_list[15: 20]) * 4
    trait_score_dict["Neuroticism"]= sum(responses_list[20: 25]) * 4

    # Radar (Spider) Chart
    traits= list(trait_score_dict.keys())
    values= list(trait_score_dict.values())
    # Number of variables
    num_vars = len(traits)
    # Compute angle for each trait
    angles = numpy.linspace(start= 0, stop= (2 * numpy.pi), num= num_vars, endpoint= False).tolist()
    # Make the plot circular
    values += values[:1]
    angles += angles[:1]
    # Create the radar chart
    fig, ax = plt.subplots(figsize= (6, 6), dpi= 100, subplot_kw= dict(polar= True))
    ax.fill(angles, values, color= "green", alpha= 0.25)
    ax.plot(angles, values, color= "green", linewidth= 3)
    # Add labels for each axis
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(traits, fontsize=12)
    # Title
    plt.title("Radar (Spider) chart", size=14, color= "black", y= 1.1)
    plt.savefig(os.path.join(os.getcwd(), "static", "radar_chart.png"))
    return trait_score_dict

def show_trait_responses(candidate_username):
    connection= sqlite3.connect(os.path.join(os.getcwd(), "Database", "personality_database.db"))
    cursor= connection.cursor()
    cursor.execute(f"""SELECT Datalist, Name FROM Personality_data WHERE Username= {'"' + candidate_username + '"'};""")
    datalist= cursor.fetchall()[0]
    scores_list, candidate_name= datalist[0], datalist[1]
    scores_list= ast.literal_eval(node_or_string= scores_list)

    trait_score_dict= {trait: 0 for trait in text_data.big_five_traits_dict.keys()}
    trait_score_dict["Openness"]= sum(scores_list[0: 5]) * 4
    trait_score_dict["Conscientiousness"]= sum(scores_list[5: 10]) * 4
    trait_score_dict["Extraversion"]= sum(scores_list[10: 15]) * 4
    trait_score_dict["Agreeableness"]= sum(scores_list[15: 20]) * 4
    trait_score_dict["Neuroticism"]= sum(scores_list[20: 25]) * 4
    
    cursor.execute("""SELECT Username, Datalist FROM Personality_data;""")
    datalist= [x for x in cursor.fetchall()]
    connection.close()
    other_candidates_trait_score_dict= {trait: 0 for trait in text_data.big_five_traits_dict.keys()}
    n= 0
    for element in datalist:
        if element[0] != candidate_username:
            scores_list= ast.literal_eval(node_or_string= element[1])
            other_candidates_trait_score_dict["Openness"] += sum(scores_list[0: 5]) * 4
            other_candidates_trait_score_dict["Conscientiousness"] += sum(scores_list[5: 10]) * 4
            other_candidates_trait_score_dict["Extraversion"] += sum(scores_list[10: 15]) * 4
            other_candidates_trait_score_dict["Agreeableness"] += sum(scores_list[15: 20]) * 4
            other_candidates_trait_score_dict["Neuroticism"] += sum(scores_list[20: 25]) * 4
            n += 1
    other_candidates_trait_score_dict= {trait: int(other_candidates_trait_score_dict[trait]/n) for trait in other_candidates_trait_score_dict.keys()}
    
    # Radar (Spider) Chart
    traits= list(trait_score_dict.keys())
    values= list(trait_score_dict.values())
    # Number of variables
    num_vars = len(traits)
    # Compute angle for each trait
    angles = numpy.linspace(start= 0, stop= (2 * numpy.pi), num= num_vars, endpoint= False).tolist()
    # Make the plot circular
    values += values[:1]
    angles += angles[:1]
    # Create the radar chart
    fig, ax = plt.subplots(figsize= (6, 6), dpi= 100, subplot_kw= dict(polar= True))
    ax.fill(angles, values, color= "green", alpha= 0.25)
    ax.plot(angles, values, color= "green", linewidth= 3)
    # Add labels for each axis
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(traits, fontsize=12)
    # Title
    plt.title("Radar (Spider) chart", size=14, color= "black", y= 1.1)
    plt.savefig(os.path.join(os.getcwd(), "static", "radar_chart.png"))
    return (candidate_name, trait_score_dict, other_candidates_trait_score_dict)
