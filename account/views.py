from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
import pandas as pd
import random
from django.core.mail import EmailMessage
# Create your views here.

def sendEmail(emailto, passwd):
    html_content = f"If you are receiving this email. You an eligible voter and a member of IESA. Email: {emailto}, password: {passwd}"
    sub = f"Login Details For IESA Election"
    email = EmailMessage(sub, html_content, 'Cypherspot <do_not_reply@domain.com>', [emailto])
    email.content_subtype = "html"

    email.send()
    return "sent successfully"

def sendMassEmail(file_path):
    df = pd.read_excel(file_path)

    data = []

    for l in range(0, int(df.size / 2)):
        m = []
        for i in df.iloc[l]:
            m.append(i)
        data.append(m)

    for i in data:
        sendEmail(i[0], i[1])

    print("done")
    return "done"

def generate_random():
    random_string = ''

    for _ in range(10):
        # Considering only upper and lowercase letters
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        # Convert to lowercase if the flip bit is on
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))

    return random_string

def add_to_db(file_path):
    df = pd.read_excel(file_path)

    data = []

    for l in range(0, int(df.size / 15)):
        m = []
        for i in df.iloc[l]:
            m.append(i)
        data.append(m)

    email_passwd = dict()
    u = 1
    for i in data:
        passwd = generate_random()
        datum = {
            "last_name": i[3].split()[0],
            "first_name": i[3].split()[-1],
            "email": i[4],
            "password": passwd
        }
        # print(datum, u)
        u += 1
        userForm = CustomUserForm(datum or None)
        voterForm = VoterForm({"phone": str(i[5])} or {"phone": "09011234"})
        user = userForm.save(commit=False)
        voter = voterForm.save(commit=False)
        voter.admin = user
        user.save()
        voter.save()
        email_passwd[i[4]] = passwd
    df = pd.DataFrame(data=email_passwd, index=[0])

    df = (df.T)

    print (df)

    df.to_excel('dict1.xlsx')
    print("Added successfully!")
    return "Added successfully"

def account_login(request):
    # add_to_db('students_data.xlsx')
    # sendMassEmail(file_path)
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)


def account_register(request):
    if request.method == 'GET':
        return redirect(reverse('account_login'))
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
            # return account_login(request)
    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))
