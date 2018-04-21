# 364final
Python Flask Application where user can search for medical marijuana strains and add them save medical marijuana strains in their account.
# 364final
Python Flask Application where user can search for medical marijuana strains and add them save medical marijuana strains in their account. A user has to register before they are able to log in or see anyt of the routes outside of **/register** and **/login**. Once the person creates and account and logs in, they are redirected to the **/** route where the user can select to seaerch for medical marijuana strains by the name of a strain, a flavor, or a strain effect. The app dispalys first 5 responses, or less, and then the user has the ability to save it to their "Medical Marijuana WishList" or their "Tried" strains. User's can also rank the strains on a scale of 1-5 and update the ranking as they please

## Import Requirements
`pip install flask_login`
`pip install flask`
`pip install flask_script`
`pip install flask_wtf`
`pip install wtforms`
`pip install wtforms.validators`
`pip installwtforms.fields.html5`
`pip install flask_sqlalchemy`
`pip install flask_migrate`
`pip install werkzeug.security`

### How to Run the File
Make sure you have an API-KEY form **http://strains.evanbusse.com/** and save it in python file call `mj_api.py` in a variable called API_KEY. Import the API_KEY variable into the `practice_api.py` file. After that, make sure you have all the above requirements installed. Finally create a local database called `FRGAsi364final`. Finally, travel to command prompt and type `pyton si364final.py runserver`. After this, you need to register for an account so travel to the /register route. Enter your email(twice) and your password (twice). If the HTML is validated, then you are redirected to the "/login" route where you can sign-in using the password and email you just used. Once you are logged in, you are redirected to the index route. There you can select a radio field option like **name** and then type in "OG Kush" hit enter. Then you will be redirected to a **/<type>/query/<search>** route, where data will be displayed.
Once you read the data, you can decide to add any of the medical marijuana strains to a saved list, a **Wishlist** or a **Tried** list. The Wishlist is a list of strains where the user would like to try in the future. The Tried list is a list a medical marijuana strains that the user has already tried before. After this, the user is redirected to **/collection/<type_list>** route. The type_list route is either the Wishlist of the Tried list that the user decided to add strains into. There, the user can click on the strains that the any strain that is saved in the list and it will redirect them to a new page where the user can ready more about the strain (its race, description, effects, and flavors). The page will also display a HTML form where the user can deicde how important that strain is to them (on a scale of 1-5, 5 is the highest level of importance). A five means that the user would like to try that or liked it more then other strains. Once the user updates the strain's ranking and the form is validated, then the user is redirect back to view all of their lists of strains (Tried or Wishlist). The user also has the opportunity to delete a strain from the list if they choose to by clickin on a a list and then clicking the delete button underneath the link to view more information about a specific saved strain. Finally, the user can log out.

### All Routes and HTML Templates

`/` -> `index.html` Displays an HTML form to search for Medical Marijuana Strains - creates a Search object in the PastSearches model
`/<type>/query/<search>` -> `display_results.html` Displays the first 5 or less items from the API response. Also displays an HTML template that allows the user to Save results into a set of two lists
`/collections` -> `collections.html` Displays the name of collected "list" of strains the user has saved
`/collection/<type_lst>` -> `collection.html` Displays the name of the Medical Marijuana Strain saved in that list
`/collection/<saved_list>/<name>` -> `view_strain.html` Displays more information about a specifi strain. Also displays an HTML form where the user can update a strain's ranking (1-5)
`/strain/<name>/update/` -> No HTML template; redirects back to `/collections` If the form is submitted via a GET method, will update the ranking of a Medical Marijuana Strain
`/delete/<name>` -> No HTML template; redirects back to `/collections` If the form is submitted via a GET method, will delete the strain instance from the database
`/logout/` -> No HTML template; redirects back to `/login` Will log the user out
`/login` -> `/login.html` Allows the user to sign into their account
`/register` -> `register.html` Allows users to create an account to do anything in the app




