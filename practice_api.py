
# Francisco "Paco" Gallardo
import json
import requests
from mj_api import API_KEY



if not API_KEY:
	API_KEY = input("Please apply for an api key at strainapi.evanbusse.com and paste it here")
SEARCH_BASEURL = 'http://strainapi.evanbusse.com/{}/strains/'.format(API_KEY)

# I will only call this function if the search_by_name() function does not return None
def search_strain_effects(s_id):
	url = SEARCH_BASEURL + 'data/effects/' + str(s_id)
	# print(url)
	resp = requests.get(url)
	resp_obj = resp.json()
	if resp_obj['positive'] != []:
		positive_effects = resp_obj['positive']
	else:
		positive_effects = None # Return none so that when I call my get_or_create_effects helper function to add a new effect to my database, it will not actually add None to the database
	if resp_obj['negative'] != []:
		negative_effects = resp_obj['negative']
	else:
		negative_effects = None # Return none so that when I call my get_or_create_effects helper function to add a new effect to my database, it will not actually add None to the database
	if resp_obj['medical'] != []:
		med_effects = resp_obj['medical']
		print(med_effects)
	else:
		med_effects = None # Return none so that when I call my get_or_create_effects helper function to add a new effect to my database, it will not actually add None to the database
	return positive_effects, negative_effects, med_effects 

# I will only call this function if the search_by_name() function does not return None
def search_strain_flavors(s_id):
	url = SEARCH_BASEURL + 'data/flavors/' + str(s_id)
	# print(url)
	resp = requests.get(url)
	resp_obj = resp.json()
	if resp_obj != []:
		return resp_obj
	else:
		return None # Return none so that when I call my get_or_create_flavor helper function to add a new flavor to my database, it will not actually add None to the database
def search_strain_desc(s_id):
	url = SEARCH_BASEURL + "data/desc/" + str(s_id)
	resp = requests.get(url)
	resp_obj = resp.json()
	if resp_obj and resp_obj['desc']:
		return resp_obj['desc']
	else:
		return None

# I will call this functions witihin the /<type>/query/<search> route and only when type is 'name'
def search_by_name(name):
	url = SEARCH_BASEURL + "search/name/" + name
	# print(url) 
	resp = requests.get(url)
	resp_obj = resp.json()
	strain_info = {}
	if resp_obj != []:

		
		for strain in resp_obj[:5]:
			strain_name = strain['name']
			strain_id = strain['id']
			strain_race = strain['race']
			strain_description  = strain['desc']

			flavors_resp = search_strain_flavors(strain_id)
			if flavors_resp:
				flavors = flavors_resp
			else:
				flavors = None

			effects_resp = search_strain_effects(strain_id)
			if effects_resp[0]:
				# print(effects_resp[0])
				positive_effects = effects_resp[0]
			else:
				positive_effects = None
			if effects_resp[1]:
				# print(effects_resp[1])
				negative_effects = effects_resp[1]
			else:
				negative_effects = None
			if effects_resp[2]:
				# print(effects_resp[2])
				med_effects = effects_resp[2]
			else:
				med_effects = None


			strain_info[strain_name] = [strain_id, strain_race, strain_description, flavors, positive_effects, negative_effects, med_effects]
		return strain_info
		# If this returns the correct data, then I will use the the strain_id variable to make another API request to get the the strains flavor and effect information
	else:
		return None


# I will call this functions witihin the /<type>/query/<search> route and only when type is 'flavor'
def search_by_flavor(flavor): # try using strawberry as an input to get some data
	url = SEARCH_BASEURL + "search/flavor/" + flavor
	# print(url)
	resp = requests.get(url)
	resp_obj = resp.json()
	strain_info = {}
	if resp_obj != []:
		for strain in resp_obj[:5]:
			strain_name = strain['name']
			strain_id = strain['id']
			strain_race = strain['race']

			flavors_resp = search_strain_flavors(strain_id)
			if flavors_resp:
				flavors = flavors_resp
			else:
				flavors = None

			effects_resp = search_strain_effects(strain_id)
			if effects_resp[0]:
				positive = effects_resp[0]
			else:
				positive = None
			if effects_resp[1]:
				negative = effects_resp[1]
			else:
				negative = None
			if effects_resp[2]:
				med = effects_resp[2]
			else:
				med = None

			if search_strain_desc(strain_id):
				strain_description = search_strain_desc(strain_id)
			else:
				strain_description = None

			strain_info[strain_name] = [strain_id, strain_race, strain_description, flavors, positive, negative, med]
		return strain_info
		# If this returns the correct data, then I will use the the strain_id variable to make another API request to get the the strains desciption and effect information
	else:
		return None

# I will call this functions witihin the /<type>/query/<search> route and only when type is 'effect'
def search_by_effect(effect): 
	url = SEARCH_BASEURL + "search/effect/" + effect #try using happy as an input to get some data
	# print(url)
	resp = requests.get(url)
	resp_obj = resp.json()
	strain_info = {}
	if resp_obj != []:
		for strain in resp_obj[:5]:
			strain_name = strain['name']
			strain_id = strain['id']
			strain_race = strain['race']
			flavors_resp = search_strain_flavors(strain_id)
			if flavors_resp:
				flavors = flavors_resp
			else:
				flavors = None

			effects_resp = search_strain_effects(strain_id)
			if effects_resp[0]:
				positive = effects_resp[0]
			else:
				positive = None
			if effects_resp[1]:
				negative = effects_resp[1]
			else:
				negative = None
			if effects_resp[2]:
				med = effects_resp[2]
			else:
				med = None

			if search_strain_desc(strain_id):
				strain_description = search_strain_desc(strain_id)
			else:
				strain_description = None



			strain_info[strain_name] = [strain_id, strain_race, strain_description, flavors, positive, negative, med]
		return strain_info
		# If this returns the correct data, then I will use the the strain_id variable to make another API request to get the the strains descrption and flavor information
	else:
		return None

# Once the information is retrieved using these functions, then I will add the strain and its attributes to the specific model table

###### Pratice Invocations ##########
# Once I get the return values of these functions below, then I will add use the return values to pass them into 
# my helper functions that will create strains, effects and flavors
# strain_info = search_by_name('blue')
# effects = search_strain_effects(strain_info[1])
# flavors = search_strain_flavors(strain_info[1])
# print(strain_info)
# print()
# print(effects)
# print()
# print(flavors)


# #### MORE SAMPLE INVOCATIONS 
# print(search_by_effect('headache'))
# print()
# print(search_by_flavor('strawberry'))

