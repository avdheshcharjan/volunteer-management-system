# Volunteer Management Bot Documentation

## 1. Register Organization

**Command:** `/register_org`

**Description:** Admin registers a new organization.

**Bot Response:**
Organization registered successfully!
Your organization code is: <org_code>


---

## 2. Volunteer Signup

**Command:** `/volunteer_signup`

**Description:** Volunteers sign up using the organization code.

**Bot Response:**
Signup successful! You are now registered as a volunteer.
You can indicate your availability using the command: /indicate_availability
Format: {"monday": ["10:00-14:00"], "tuesday": ["09:00-17:00"]}


---

## 3. Indicate Availability

**Command:** `/indicate_availability`

**Description:** Volunteers indicate their availability.

**Bot Workflow:**
1. **Bot Asks for Availability:**
Please provide your availability in the following format: {"monday": ["10:00-14:00"], "tuesday": ["09:00-17:00"]}

2. **Volunteer Provides Availability:**

3. **Bot Asks for Confirmation:**
You have indicated the following availability:
<monday: 10:00-14:00, tuesday: 09:00-17:00>
Do you want to confirm this? (yes/no)

4. **Volunteer Confirms:**

5. **Bot Updates Database and Responds:**
Your availability has been updated successfully!


---

## 4. Beneficiary Signup

**Command:** `/beneficiary_signup`

**Description:** Beneficiary sign up using the organization code.

**Bot Response:**
Signup successful! You have been registered as a beneficiary.

**Admin Notification:**
New beneficiary signup: <beneficiary_name> needs help on <date> at <time>. Help needed: <help_needed>


---

## 5. Update Needs

**Command:** `/update_needs`

**Description:** Beneficiarys update their need date.

**Bot Workflow:**
1. **Bot Asks for New Date and Time:**
Please provide the new date and time for your needs in the format: YYYY-MM-DD HH

2. **Beneficiary Provides New Date and Time:**

3. **Bot Updates Database and Responds:**
Your needs date has been updated successfully!


---

## 6. Get Available Volunteers

**Command:** `/get_available_volunteers`

**Description:** Get all available volunteers based on date and time.

**Bot Workflow:**
1. **Bot Asks for Date and Time:**
Please provide the date and time to check for available volunteers in the format: YYYY-MM-DD HH

2. **Admin Provides Date and Time:**

3. **Bot Responds with Available Volunteers:**
Available volunteers for <date> at <time>:

Volunteer 1
Volunteer 2

---

## 7. Assign Volunteer to Beneficiary

**Command:** `/assign`

**Description:** Admin assigns a volunteer to a beneficiary at a specific date and time.

**Bot Workflow:**
1. **Bot Asks for Beneficiary Name and Volunteer Name:**
Please provide the beneficiary's name and the volunteer's name to assign, in the format: beneficiary_name, volunteer_name

2. **Admin Provides Beneficiary Name and Volunteer Name:**

3. **Bot Checks and Responds:**
   - **If Successful:**
Volunteer assigned successfully!

**Notifications:**
- **To Volunteer:**
You have been assigned to help <beneficiary_name> on <date> at <time>.

- **To Beneficiary:**
<volunteer_name> has been assigned to assist you on <date> at <time>.

---

## 8. Show Unattended Beneficiaries

**Command:** `/show_unattended`

**Description:** Show beneficiaries who have not yet attended, with their date and time.

**Bot Response:**
Unattended beneficiaries:

Beneficiary 1: <date> at <time>
Beneficiary 2: <date> at <time>

