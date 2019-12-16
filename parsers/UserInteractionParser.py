#!/usr/bin/env python
# coding: utf-8



import xml.etree.ElementTree as etree
import codecs
from collections import namedtuple 
from datetime import datetime

# Capture All information with one user interaction, we might have to add session number also
UserInteraction = namedtuple("UserInteraction", "query, start_time, interaction_number, search_results, user_clicks")
# One search result representing one doc with its rank, to be used with UserInteraction
SearchResult = namedtuple("SearchResult", "rank, url, clueweb09_id, snippet, title")
# Document information of the clicked item.
UserClicks = namedtuple("UserClicks", "num, rank, start_time, end_time, clueweb09_id")

def parse_topic(topic):
    """
    TODO: 
    """
    pass

def parse_click(click):
    """
    Parses following xml element:
    <click num="1" starttime="15:06:02.870068" endtime="15:06:11.579471">
        <rank>1</rank>
    </click>
    """
    num = int(click.attrib['num'])
    rank_of_doc = int(click.find('rank').text)
    start_time = datetime.strptime(click.attrib['starttime'], "%H:%M:%S.%f") # 15:06:11.579471
    end_time = datetime.strptime(click.attrib['endtime'], "%H:%M:%S.%f") # 15:06:11.579471
    clueweb09_id = None # To be mapped from SearchResult using the rank_of_doc
    return UserClicks(num, rank_of_doc, start_time, end_time, clueweb09_id)

def parse_interaction(interaction):
    """
    parse following xml element:
    <interaction num="1" starttime="09:54:27.674484">
         <query>US tax code 403 (b)</query>
         <results>
            <result rank="1">
               <url>http://en.wikipedia.org/wiki/403(b)</url>
               <clueweb09id>clueweb09-enwp00-09-05733</clueweb09id>
               <title>403(b) - Wikipedia, the free encyclopedia</title>
               <snippet>The Employee Retirement Income Security Act (ERISA) does not require 403(b) plans to be technically qualified plans, i.e., plans governed by US Tax Code 401(a), but have ...</snippet>
            </result>
            <result rank="2">
               <url>http://en.wikipedia.org/wiki/Internal_Revenue_Code</url>
               <clueweb09id>clueweb09-enwp01-56-23264</clueweb09id>
               <title>Internal Revenue Code - Wikipedia, the free encyclopedia</title>
               <snippet>... United States Statutes at Large and as title 26 of the United States Code. Subsequent permanent tax laws ... paragraph (b) (403(b)): employer-sponsored retirement plan at ...</snippet>
            </result>
         </results>
         <clicked>
            <click num="1" starttime="09:54:42.635247" endtime="09:54:43.722679">
               <rank>2</rank>
            </click>
            <click num="2" starttime="09:54:44.273290" endtime="09:54:45.208850">
               <rank>1</rank>
            </click>
         </clicked>
      </interaction>
    
    Returns : UserInteraction which captures a user's interaction for a query and search page result.
    """
    query = interaction.find("query").text
    start_time = datetime.strptime(interaction.attrib['starttime'], "%H:%M:%S.%f") # 15:06:11.579471
    interaction_number = int(interaction.attrib['num'])
    result_list = interaction.find('results')
    search_results = [parse_search_result(result) for result in result_list]
    rank_to_clueweb09_id = {search_result.rank : search_result.clueweb09_id for search_result in search_results}
    
    clicked_list = interaction.find('clicked')
    user_clicks = []
    for click in clicked_list:
        user_click = parse_click(click)
        clueweb09_id = rank_to_clueweb09_id[user_click.rank]
        user_click_clone = UserClicks(user_click.num, user_click.rank, 
                                      user_click.start_time, user_click.end_time, 
                                      clueweb09_id)
        user_clicks.append(user_click_clone)
    
    return UserInteraction(query, start_time, interaction_number, search_results, user_clicks)
        
    
def parse_search_result(result_element):
    """
    Example XML Element to parse:
            <result rank="10">
               <url>http://www.massachusetts.edu/treasurer/403b.html</url>
               <clueweb09id>clueweb09-en0010-79-01642</clueweb09id>
               <title>403b Plan</title>
               <snippet>University of Massachusetts 403(b) Elective ... plan, frequently referred to as a Tax ... plan that operates under Section 403(b) of the Internal Revenue Code.</snippet>
            </result>
    """
    rank = int(result_element.attrib['rank'])
    url = result_element.find('url').text
    title = result_element.find('title').text
    snippet = result_element.find('snippet').text
    clueweb09_id = result_element.find('clueweb09id').text
    return SearchResult(rank, url, clueweb09_id, snippet, title)

def parse_current_query(current_query):
    """
    We have to return document recommendation for this query
    """
    pass
def parse_session_queries_2012(path_to_file="/home/ec2-user/SageMaker/data/sessiontrack2012.txt"):
    """
    Parses the user session query to generate datastructures encapsulating user interaction
    """
    target_file = codecs.open(path_to_file,mode='r',encoding='utf-8')
    content = target_file.read()
    content = content.replace("&", "&amp;");
    parser = etree.XMLParser(encoding="utf-8")
    root_doc = etree.fromstring( content, parser=parser )
    for session in root_doc:
        topic = session.find("topic") # Not being used
        interactions = session.findall("interaction")
        parsed_interactions = []
        for intaxn in interactions:
            user_interaction = parse_interaction(intaxn)   
            parsed_interactions.append(user_interaction)
            
        current_query = session.find("currentquery").text
        yield(current_query, parsed_interactions)
        
#parse_session_queries_2012()






