from django.shortcuts import render, redirect
from .models import User, Student, Teacher, Admin
from .forms import LoginForm, StudentForm, TeacherForm
from .auth_bootstrap import ensure_default_admin_exists
import numpy as np
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .utils import train_knn_model, translate_to_english
from django.shortcuts import render, redirect
from .models import User, Student, Teacher, Admin, Message
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Login view
def login_view(request):
    # Import the custom User model locally to avoid being shadowed by
    # the module-level `User = get_user_model()` assignments below.
    from myapp.models import User as CustomUser
    ensure_default_admin_exists()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = CustomUser.objects.get(email=email, password=password)
                # Store user_id in session so other views can identify the logged-in user
                request.session['user_id'] = user.id
                request.session['user_type'] = user.user_type
                x = user.id - 1
                if user.user_type == 'student':
                    return redirect(f'/student/{x}/dashboard/')
                elif user.user_type == 'teacher':
                    return redirect(f'/teacher/{user.id}/dashboard/')
                elif user.user_type == 'admin':
                    return redirect(f'/ads/{user.id}/dashboard/')
            except CustomUser.DoesNotExist:
                # Handle incorrect login
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Clear the session and redirect to the login page."""
    request.session.flush()
    return redirect('login')



from django.shortcuts import render
from .models import Student
from django.db.models import Avg

def student_dashboard(request, student_id):
    stx = student_id - 2
    student = Student.objects.get(id=stx)

    # Get all students in the same class
    class_students = Student.objects.filter(class_name=student.class_name)

    # Calculate mean values for absences, study time, and G3 score in the same class
    mean_absences = class_students.aggregate(Avg('absences'))['absences__avg']
    mean_studytime = class_students.aggregate(Avg('studytime'))['studytime__avg']
    mean_G3 = class_students.aggregate(Avg('G3'))['G3__avg']

    # Pass student data and calculated mean values to the template
    return render(request, 'student_dashboard.html', {
        'student': student,
        'mean_absences': mean_absences,
        'mean_studytime': mean_studytime,
        'mean_G3': mean_G3,
    })


from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Teacher, Student, Message

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Teacher, Student, Message
from django.db.models import Q

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Count, Q
from .models import Teacher, Student, Message

def teacher_dashboard(request, user_id):
    # Get the teacher based on user_id
    teacher = get_object_or_404(Teacher, user_id=user_id)

    # Fetch all students associated with this teacher
    students = Student.objects.filter(teacher=teacher)

    # Categorize students based on their results
    students_zero = students.filter(result=0).count()  # Students with result 0
    students_one = students.filter(result=1).count()  # Students with result 1
    students_other = students.exclude(result__in=[0, 1]).count()  # Students with other results

    # Fetch all messages related to the teacher
    messages = Message.objects.filter(
        Q(sender__email=request.user.email) | Q(recipient__email=request.user.email)
    )

    # Send the categorized data to the template
    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'students': students,
        'messages': messages,
        'students_zero': students_zero,
        'students_one': students_one,
        'students_other': students_other,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Student, Teacher, Admin, Message, Class
from .forms import StudentForm, TeacherForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.http import JsonResponse


from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Admin, Student, Teacher, Class, Message

def admin_dashboard(request, user_id):
    admin = get_object_or_404(Admin, user_id=user_id)
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    classes = Class.objects.all()

    # Calculate totals
    total_students = students.count()
    total_teachers = teachers.count()
    total_classes = classes.count()

    # Students at risk (result = 0)
    students_at_risk = students.filter(result=0)
    students_at_risk_count = students_at_risk.count()
    students_not_at_risk_count = total_students - students_at_risk_count

    # Teachers at risk (teaching students with result = 0)
    teachers_at_risk_count = teachers.filter(student__result=0).distinct().count()
    teachers_not_at_risk_count = total_teachers - teachers_at_risk_count

    # Count students with result = 0 per teacher
    teacher_student_counts = [
        {'teacher': teacher, 'zero_count': students_at_risk.filter(teacher=teacher).count()}
        for teacher in teachers
    ]
    teacher_student_counts.sort(key=lambda x: x['zero_count'], reverse=True)

    if request.method == 'POST' and 'send_message_to_teacher' in request.POST:
        teacher_id = request.POST['teacher']
        message_content = request.POST['message']
        # Translate message to English if it is in another language
        message_content = translate_to_english(message_content)
        teacher = get_object_or_404(Teacher, id=teacher_id)
        Message.objects.create(
            sender=request.user,
            recipient=teacher.user,
            content=message_content,
            message_type='admin_to_teacher'
        )

    return render(request, 'admin_dashboard.html', {
        'admin': admin,
        'students': students,
        'teachers': teachers,
        'classes': classes,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'students_at_risk_count': students_at_risk_count,
        'students_not_at_risk_count': students_not_at_risk_count,
        'teachers_at_risk_count': teachers_at_risk_count,
        'teachers_not_at_risk_count': teachers_not_at_risk_count,
        'teacher_student_counts': teacher_student_counts,
        'students_with_zero_result': students_at_risk,
    })


from django.http import HttpResponse


from .models import Student, Message





from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
import io


def generate_report(request, student_id):
    from xhtml2pdf import pisa

    # Fetch student data
    student = get_object_or_404(Student, id=student_id)

    # Fetch student messages (if any)
    messages = Message.objects.filter(recipient=student.user)
    message_content = "\n".join([f"{msg.sent_at.strftime('%Y-%m-%d')} - {msg.content}\n" for msg in messages]) if messages.exists() else "No recommendations available."

    # Prepare the data dictionary for the HTML template
    form_data = {
        "name": student.name,
        "familyname": student.familyname,
        "teacher": student.teacher.name,
        "class_name": student.class_name.name,
        "age": student.age,
        "sex": student.sex,
        "guardian": student.guardian,
        "address": student.address,
        "famsize": student.famsize,
        "Pstatus": student.Pstatus,
        "Medu": student.Medu,
        "Fedu": student.Fedu,
        "Mjob": student.Mjob,
        "Fjob": student.Fjob,
        "reason": student.reason,
        "traveltime": student.traveltime,
        "studytime": student.studytime,
        "failures": student.failures,
        "famrel": student.famrel,
        "freetime": student.freetime,
        "goout": student.goout,
        "Dalc": student.Dalc,
        "Walc": student.Walc,
        "health": student.health,
        "absences": student.absences,
        "schoolsup": student.schoolsup,
        "famsup": student.famsup,
        "paid": student.paid,
        "activities": student.activities,
        "nursery": student.nursery,
        "higher": student.higher,
        "internet": student.internet,
        "romantic": student.romantic,
        "G1": student.G1,
        "G2": student.G2,
        "messages": message_content,
    }

    # Render the HTML template with the data
    html_string = render_to_string('student_report_template.html', form_data)

    # Convert the HTML to PDF
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_string), dest=pdf_file)
    
    if pisa_status.err:
        return HttpResponse("Error generating PDF", content_type="text/plain")

    # Return the PDF as a response
    pdf_file.seek(0)
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="student_report_{student_id}.pdf"'
    
    return response



import io
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Teacher, Student
from datetime import datetime

def generate_teacher_report(request, teacher_id):
    from xhtml2pdf import pisa

    # Fetch teacher data
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    # Fetch all students in the teacher's classes
    students = Student.objects.filter(class_name__in=teacher.classes.all())
    
    # Categorize students by result
    students_result_0 = students.filter(result=0)
    students_result_1 = students.filter(result=1)
    students_result_other = students.exclude(result__in=[0, 1])

    # Prepare data for the template
    form_data = {
        "name": teacher.name,
        "familyname": teacher.familyname,
        "phone": teacher.phone,
        "address": teacher.address,
        "hiredate": teacher.hiredate.strftime('%Y-%m-%d'),
        "subject": teacher.subject,
        "classes": ", ".join([cls.name for cls in teacher.classes.all()]),
        "students_result_0": students_result_0,
        "students_result_1": students_result_1,
        "students_result_other": students_result_other,
        "qr": r"C:\Users\pc\Desktop\myproject\myapp\static\QRID_IDAA23_25.png",  # Path to the QR code image
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "logo": r"C:\Users\pc\Desktop\myproject\myapp\static\azee.png"
    }
    form_data["pie_chart"] = generate_pie_chart(students_result_0, students_result_1, students_result_other)

    # Render HTML template
    html_string = render_to_string('teacher_report_template.html', form_data)

    # Convert HTML to PDF
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_string), dest=pdf_file)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", content_type="text/plain")

    # Return the PDF response
    pdf_file.seek(0)
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="teacher_report_{teacher_id}.pdf"'

    return response



from django.shortcuts import render
from .models import Admin, Teacher, Student, Class
import qrcode
import base64
from io import BytesIO
from datetime import date

def generate_qr_code(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{qr_base64}'

from django.shortcuts import render, get_object_or_404
from .models import Admin, Teacher, Student, Class
from datetime import date
from django.http import HttpResponse
from django.conf import settings

def admin_report(request, admin_id):
    from xhtml2pdf import pisa

    # Fetch the admin data
    admin = get_object_or_404(Admin, id=admin_id)
    
    # Fetch total counts of teachers, students, and classes
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()
    total_classes = Class.objects.count()
    
    # Fetch students based on results
    total_students_result_0 = Student.objects.filter(result=0).count()
    total_students_result_1 = Student.objects.filter(result=1).count()

    # Path to pre-generated QR code image
    qr_image_path = r"C:\Users\pc\Desktop\myproject\myapp\static\QRID_IDAA23_25.png"

    # Prepare data for the template
    context = {
        'admin': admin,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_classes': total_classes,
        'total_students_result_0': total_students_result_0,
        'total_students_result_1': total_students_result_1,
        'qr': qr_image_path,  # Direct path to the pre-generated QR code image
        'report_date': date.today().strftime('%Y-%m-%d'),
        'logo': r"C:\Users\pc\Desktop\myproject\myapp\static\azee.png",  # Path to the logo image
    }

    # Prepare HTML string from template
    html_string = render_to_string('ads_report_template.html', context)

    # Convert HTML to PDF
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", content_type="text/plain")

    # Return the PDF response
    pdf_file.seek(0)
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="admin_report_{admin_id}.pdf"'

    return response


# Student Views
import matplotlib.pyplot as plt
import base64

# Generate Pie Chart
def generate_pie_chart(students_result_0, students_result_1, students_result_other):
    labels = ["Result = 0", "Result = 1", "Other"]
    sizes = [students_result_0.count(), students_result_1.count(), students_result_other.count()]
    colors = ["#FF5733", "#33FF57", "#337BFF"]

    plt.figure(figsize=(4, 4))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
    plt.axis("equal")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()



from django.shortcuts import render, redirect
from .models import Message, Teacher
from django.contrib.auth import get_user_model

User = get_user_model()

def send_message_to_teacher(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        message_content = request.POST.get('message')

        # Check if teacher_id and message_content are provided
        if teacher_id and message_content:
            # Translate message to English before saving
            message_content = translate_to_english(message_content)
            try:
                from myapp.models import User as CustomUser
                # Fetch the teacher instance using the provided teacher_id
                teacher = Teacher.objects.get(id=teacher_id)

                # Resolve the custom User instance (not Django's auth.User)
                sender = CustomUser.objects.get(email=request.user.email) if hasattr(request, 'custom_user') else CustomUser.objects.get(id=request.session.get('user_id'))

                # Create the message and assign sender and recipient
                message = Message(
                    sender=sender,
                    recipient=teacher.user,
                    content=message_content,
                    message_type='admin_to_teacher'
                )
                message.save()

                return redirect('admin_dashboard', user_id=sender.id)

            except Teacher.DoesNotExist:
                return render(request, "error.html", {"error": "Teacher not found"})
            except Exception as e:
                return render(request, "error.html", {"error": f"Error sending message: {e}"})

    # Fallback redirect
    user_id = request.session.get('user_id', 1)
    return redirect('admin_dashboard', user_id=user_id)

from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import Message, Student

User = get_user_model()

def send_message_to_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        message_content = request.POST.get('message')

        if not student_id or not message_content:
            return render(request, "error.html", {"error": "Student or message content missing"})

        # Translate message to English before saving
        message_content = translate_to_english(message_content)

        try:
            from myapp.models import User as CustomUser
            student = Student.objects.get(id=student_id)

            # BUG FIX: get teacher via the session's custom user_id,
            # not via request.user (Django auth.User) which has a different ID space.
            teacher_user_id = request.session.get('user_id')
            teacher = Teacher.objects.get(user_id=teacher_user_id)

            Message.objects.create(
                sender=teacher.user,
                recipient=student.user,
                content=message_content,
                message_type='teacher_to_student'
            )

            return redirect('teacher_dashboard', user_id=teacher_user_id)

        except Student.DoesNotExist:
            return render(request, "error.html", {"error": "Student not found"})
        except Teacher.DoesNotExist:
            return render(request, "error.html", {"error": "Teacher not found. Please log in again."})

    user_id = request.session.get('user_id', 1)
    return redirect('teacher_dashboard', user_id=user_id)

# Helper to get all messages for a user
def get_received_messages(user):
    return Message.objects.filter(recipient=user).order_by('-sent_at')

from django.shortcuts import render, get_object_or_404
from .models import Message, Admin

from django.shortcuts import render, get_object_or_404
from .models import Message, Admin
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Student, Teacher, Admin, Message
from .forms import LoginForm, StudentForm, TeacherForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Login view

# Admin Dashboard View

from django.shortcuts import render, redirect
from .forms import TeacherForm, StudentForm, UserForm
from .models import User

def create_teacher(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        teacher_form = TeacherForm(request.POST)
        if user_form.is_valid() and teacher_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 'teacher'
            user.save()
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            # Translate free-text fields to English
            teacher.name = translate_to_english(teacher.name)
            teacher.familyname = translate_to_english(teacher.familyname)
            teacher.address = translate_to_english(teacher.address)
            teacher.subject = translate_to_english(teacher.subject)
            teacher.save()
            teacher_form.save_m2m()
            return redirect('teacher_list')
    else:
        user_form = UserForm()
        teacher_form = TeacherForm()

    return render(request, 'create_teacher.html', {'user_form': user_form, 'teacher_form': teacher_form})

def create_student(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 'student'
            user.save()
            student = student_form.save(commit=False)
            student.user = user
            # Translate free-text fields to English
            student.name = translate_to_english(student.name)
            student.familyname = translate_to_english(student.familyname)
            if student.address:
                student.address = translate_to_english(student.address)
            student.save()
            return redirect('student_list')
    else:
        user_form = UserForm()
        student_form = StudentForm()

    return render(request, 'create_student.html', {'user_form': user_form, 'student_form': student_form})


def create_class(request):
    """Render the create class form and handle submissions."""
    if request.method == "POST":
        class_name = request.POST.get("name")
        if class_name:
            new_class, created = Class.objects.get_or_create(name=class_name)
            if created:
                return redirect('create_class')  # Redirect after successful creation
            else:
                return JsonResponse({"error": "Class already exists."}, status=400)
    return render(request, 'create_class.html')

    

from django.shortcuts import render
from .models import Student  # Import your Student model

def student_list(request):
    students = Student.objects.all()
    return render(request, 'students_list.html', {'students': students})


from django.shortcuts import render
from .models import Teacher  # Import your Student model

def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'teachers_list.html', {'teachers': teachers})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Teacher, User
from .forms import StudentUpdateForm, TeacherUpdateForm, UserUpdateForm

def student_update(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_update', student_id=student.id)  # Redirect to the student's profile or dashboard
    else:
        form = StudentUpdateForm(instance=student)
    return render(request, 'student_update.html', {'form': form})

def teacher_update(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_update', teacher_id=teacher.id)  # Redirect to the teacher's dashboard
    else:
        form = TeacherUpdateForm(instance=teacher)
    return render(request, 'teacher_update.html', {'form': form})

def admin_update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('ads_student_update', student_id=student.id)  # Redirect to the student's profile or dashboard
    else:
        form = StudentUpdateForm(instance=student)
    return render(request, 'ads_student_update.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Teacher
from .forms import TeacherUpdateForm

def admin_update_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('ads_teacher_update', teacher_id=teacher.id)  # Redirect to the teacher's dashboard
    else:
        form = TeacherUpdateForm(instance=teacher)
    return render(request, 'ads_teacher_update.html', {'form': form})

from django.shortcuts import render
import pickle



import pickle
import numpy as np
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Student

# Helper function to load the model
def load_model():
    with open('random_forest_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

def predict_student_result(request, student_id):
    # Load the model
    model = load_model()

    # Retrieve student data
    student = get_object_or_404(Student, id=student_id)

    # Prepare the data for prediction
    features = [
        student.age,
        student.Medu,
        student.Fedu,
        student.traveltime,
        student.studytime,
        student.failures,
        student.famrel,
        student.freetime,
        student.goout,
        student.Dalc,
        student.Walc,
        student.health,
        student.absences,
        student.G1,  # Grade 3 (target variable)
        
        # Raw categorical variables (no encoding needed)
        student.sex,  # Assuming 'sex' is a numeric or categorical field already in the correct format
        student.famsize,  # Assuming 'famsize' is in a valid format (e.g., 'LE3', 'GT3')
        student.Pstatus,  # Assuming 'Pstatus' is in a valid format (e.g., 'T', 'A')
        student.Mjob,  # Assuming 'Mjob' is a valid field (e.g., 'teacher', 'health', etc.)
        student.Fjob,  # Assuming 'Fjob' is a valid field (e.g., 'teacher', 'health', etc.)
        student.reason,  # Assuming 'reason' is a valid field (e.g., 'course', 'home', etc.)
        student.guardian,  # Assuming 'guardian' is a valid field (e.g., 'mother', 'father', etc.)
        student.schoolsup,  # Assuming 'schoolsup' is a valid field (e.g., 'yes', 'no')
        student.famsup,  # Assuming 'famsup' is a valid field (e.g., 'yes', 'no')
        student.paid,  # Assuming 'paid' is a valid field (e.g., 'yes', 'no')
        student.activities,  # Assuming 'activities' is a valid field (e.g., 'yes', 'no')
        student.nursery,  # Assuming 'nursery' is a valid field (e.g., 'yes', 'no')
        student.higher,  # Assuming 'higher' is a valid field (e.g., 'yes', 'no')
        student.internet,  # Assuming 'internet' is a valid field (e.g., 'yes', 'no')
        student.romantic  # Assuming 'romantic' is a valid field (e.g., 'yes', 'no')
    ]

    # Make the prediction using the model
    prediction = model.predict([features])

    # Convert the prediction (which may be int64) to native int type
    prediction_value = int(prediction[0])

    # Save the result to the student's result field
    student.result = prediction_value
    student.save()

    # Return a response (you can customize this as needed)
    return JsonResponse({'student_id': student_id, 'prediction': prediction_value})






from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .models import Class
from .forms import ClassUpdateForm

def admin_update_class(request, class_name):
    class_instance = get_object_or_404(Class, name=class_name)

    if request.method == 'POST':
        form = ClassUpdateForm(request.POST, instance=class_instance)
        if form.is_valid():
            form.save()

            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Class updated successfully', 'status': 'success'})

            return redirect('ads_class_update', class_name=class_instance.name)  # Ensure this URL name exists
    else:
        form = ClassUpdateForm(instance=class_instance)

    return render(request, 'ads_class_update.html', {'form': form, 'class_instance': class_instance})

   

def delete_student(request, student_id):
    """Delete a student by ID."""
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return JsonResponse({"message": "Student deleted successfully."})

def delete_teacher(request, teacher_id):
    """Delete a teacher by ID."""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    return JsonResponse({"message": "Teacher deleted successfully."})

def delete_class(request, class_name):
    """Delete a class by name."""
    class_instance = get_object_or_404(Class, name=class_name)
    class_instance.delete()
    return JsonResponse({"message": "Class deleted successfully."})


# ---------------------------------------------------------------------------
# AJAX: Live language detection + translation endpoint
# ---------------------------------------------------------------------------

from django.views.decorators.csrf import csrf_exempt

# Map of ISO 639-1 codes → human-readable language names
LANGUAGE_NAMES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
    'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
    'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)',
    'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian',
    'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician',
    'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati',
    'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew',
    'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic',
    'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian',
    'ja': 'Japanese', 'jv': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh',
    'km': 'Khmer', 'ko': 'Korean', 'ku': 'Kurdish', 'ky': 'Kyrgyz',
    'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian',
    'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay',
    'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi',
    'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian',
    'ny': 'Nyanja (Chichewa)', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish',
    'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian',
    'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho',
    'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
    'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese',
    'sw': 'Swahili', 'sv': 'Swedish', 'tl': 'Tagalog (Filipino)', 'tg': 'Tajik',
    'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian',
    'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh',
    'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu',
}
@csrf_exempt
def detect_and_translate(request):
    """
    POST /api/detect-translate/
    Body: { "text": "..." }
    Returns: { "detected_lang": "French", "lang_code": "fr",
               "translated": "...", "is_english": false }
    Uses Google Translate's free public endpoint — no API key needed.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    import json as _json
    import requests as _req

    try:
        body = _json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    text = (body.get('text') or '').strip()
    if not text:
        return JsonResponse({'detected_lang': '', 'lang_code': '',
                             'translated': '', 'is_english': True})

    try:
        # Free Google Translate endpoint — returns detected lang at index [2]
        url = 'https://translate.googleapis.com/translate_a/single'
        params = {
            'client': 'gtx', 'sl': 'auto', 'tl': 'en',
            'dt': 't', 'q': text,
        }
        resp = _req.get(url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()

        # Extract translated text from nested list
        translated_parts = data[0] if data and data[0] else []
        translated = ''.join(
            part[0] for part in translated_parts if part and part[0]
        ) or text

        # Detected language code is at data[2]
        lang_code = data[2] if len(data) > 2 and data[2] else 'unknown'
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
        is_english = lang_code.startswith('en')

        # If English, don't show translation (just pass through)
        if is_english:
            translated = text

        return JsonResponse({
            'detected_lang': lang_name,
            'lang_code': lang_code,
            'translated': translated,
            'is_english': is_english,
        })

    except Exception as e:
        return JsonResponse({'error': f'Translation service error: {e}'}, status=500)
