
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse


import re
import string
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

# Create your views here.
from Remote_User.models import ClientRegister_Model,credit_scoring_detection,detection_ratio,detection_accuracy


def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')

def Find_Predicted_Breast_Cancer_Type_Ratio(request):
    detection_ratio.objects.all().delete()
    ratio = ""
    kword = 'Good'
    print(kword)
    obj = credit_scoring_detection.objects.all().filter(Q(Prediction=kword))
    obj1 = credit_scoring_detection.objects.all()
    count = obj.count();
    count1 = obj1.count();
    ratio = (count / count1) * 100
    if ratio != 0:
        detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio1 = ""
    kword1 = 'Poor'
    print(kword1)
    obj1 = credit_scoring_detection.objects.all().filter(Q(Prediction=kword1))
    obj11 = credit_scoring_detection.objects.all()
    count1 = obj1.count();
    count11 = obj11.count();
    ratio1 = (count1 / count11) * 100
    if ratio1 != 0:
        detection_ratio.objects.create(names=kword1, ratio=ratio1)



    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/Find_Predicted_Breast_Cancer_Type_Ratio.html', {'objs': obj})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Predicted_Breast_Cancer_Detection_Type(request):
    obj =credit_scoring_detection.objects.all()
    return render(request, 'SProvider/View_Predicted_Breast_Cancer_Detection_Type.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Predicted_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Data.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = credit_scoring_detection.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Customer_Id, font_style)
        ws.write(row_num, 1, my_row.Name, font_style)
        ws.write(row_num, 2, my_row.Age, font_style)
        ws.write(row_num, 3, my_row.Occupation, font_style)
        ws.write(row_num, 4, my_row.Annual_Income, font_style)
        ws.write(row_num, 5, my_row.Monthly_Inhand_Salary, font_style)
        ws.write(row_num, 6, my_row.Num_Bank_Accounts, font_style)
        ws.write(row_num, 7, my_row.Num_Credit_Card, font_style)
        ws.write(row_num, 8, my_row.Interest_Rate, font_style)
        ws.write(row_num, 9, my_row.Num_of_Loan, font_style)
        ws.write(row_num, 10, my_row.Type_of_Loan, font_style)
        ws.write(row_num, 11, my_row.Delay_from_due_date, font_style)
        ws.write(row_num, 12, my_row.Num_of_Delayed_Payment, font_style)
        ws.write(row_num, 13, my_row.Changed_Credit_Limit, font_style)
        ws.write(row_num, 14, my_row.Num_Credit_Inquiries, font_style)
        ws.write(row_num, 15, my_row.Credit_Mix, font_style)
        ws.write(row_num, 16, my_row.Outstanding_Debt, font_style)
        ws.write(row_num, 17, my_row.Credit_Utilization_Ratio, font_style)
        ws.write(row_num, 18, my_row.Credit_History_Age, font_style)
        ws.write(row_num, 19, my_row.Payment_of_Min_Amount, font_style)
        ws.write(row_num, 20, my_row.Total_EMI_per_month, font_style)
        ws.write(row_num, 21, my_row.Amount_invested_monthly, font_style)
        ws.write(row_num, 22, my_row.Payment_Behaviour, font_style)
        ws.write(row_num, 23, my_row.Monthly_Balance, font_style)
        ws.write(row_num, 24, my_row.Prediction, font_style)

    wb.save(response)
    return response

def Train_Test_DataSets(request):
    detection_accuracy.objects.all().delete()

    data = pd.read_csv("Datasets.csv",encoding='latin-1')

    def apply_results(label):
        if (label == 0):
            return 0  # Good
        elif (label == 1):
            return 1  # Poor

    data['Results'] = data['Label'].apply(apply_results)

    x = data['Customer_Id'].apply(str)
    y = data['Results']


    cv = CountVectorizer()

    x = cv.fit_transform(x)
    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Logistic Regression")
    from sklearn.linear_model import LogisticRegression
    reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('logistic', reg))
    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)


    print("Gradient Boosting Classifier")

    from sklearn.ensemble import GradientBoostingClassifier
    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(
        X_train,
        y_train)
    clfpredict = clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, clfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, clfpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, clfpredict))
    models.append(('GradientBoostingClassifier', clf))
    detection_accuracy.objects.create(names="Gradient Boosting Classifier",
                                      ratio=accuracy_score(y_test, clfpredict) * 100)

    # SVM Model
    print("SVM")
    from sklearn import svm
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    models.append(('svm', lin_clf))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Random Forest Classifier")
    from sklearn.ensemble import RandomForestClassifier
    rf_clf = RandomForestClassifier()
    rf_clf.fit(X_train, y_train)
    rfpredict = rf_clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, rfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, rfpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, rfpredict))
    models.append(('RandomForestClassifier', rf_clf))
    detection_accuracy.objects.create(names="Random Forest Classifier", ratio=accuracy_score(y_test, rfpredict) * 100)

    csv_format = 'Results.csv'
    data.to_csv(csv_format, index=False)
    data.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/Train_Test_DataSets.html', {'objs': obj})