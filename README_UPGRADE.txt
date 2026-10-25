CAMPUS BITES UPGRADE - INSTALLATION STEPS

IMPORTANT: Back up your current project folder first. The database upgrade is designed
to preserve existing rows, but a backup is sensible.

1. Stop Streamlit in the terminal with Ctrl+C.
2. Copy the new app.py, database.py, menu.py, and ai_recommendation.py into your
   existing canteen_preordering folder, replacing the old versions.
3. Put add_sample_menu.py in that same folder.
4. Run this command from the project folder:
       python add_sample_menu.py
   This adds the new menu dishes and skips names already present.
5. Start the app:
       python -m streamlit run app.py

ADMIN PASSWORD FOR THIS LOCAL PROTOTYPE:
    Canteen@123

The app continues to use your existing orders.py. Do not replace orders.py.

NUTRITION NOTE:
Calories, protein, and carbohydrate values are approximate estimates per serving.
They are not lab-tested and can vary based on portion size and recipe. Please adjust
them to your canteen's actual ingredients before relying on them.

SECURITY NOTE:
The admin password is hardcoded for a classroom prototype. Do not deploy publicly
without moving the password to Streamlit secrets and using proper authentication.
