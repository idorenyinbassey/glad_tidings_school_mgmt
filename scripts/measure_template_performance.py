
import os
import sys
import django
import time

# Add project directory to path so Django can find settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glad_school_portal.settings")
django.setup()

from django.template import Context, Engine
from accounting.models import TuitionFee, Payment, Expense
from students.models import StudentProfile
from django.contrib.auth import get_user_model

def measure_template_performance():
    print("Measuring template rendering performance...")
    
    # Get some data for the templates
    User = get_user_model()
    students = list(StudentProfile.objects.all()[:10])
    fees = list(TuitionFee.objects.all()[:10])
    payments = list(Payment.objects.all()[:10])
    expenses = list(Expense.objects.all()[:10])
    users = list(User.objects.all()[:10])
    
    # Simple template rendering
    simple_template = """
    {% for student in students %}
        <div>{{ student.user.first_name }} {{ student.user.last_name }} - {{ student.admission_number }}</div>
    {% endfor %}
    """
    
    # Complex template rendering with loops and filters
    complex_template = """
    <table>
        <thead>
            <tr>
                <th>Student</th>
                <th>Fee Amount</th>
                <th>Paid Amount</th>
                <th>Balance</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
        {% for fee in fees %}
            <tr>
                <td>{{ fee.student.user.first_name }} {{ fee.student.user.last_name }}</td>
                <td>{{ fee.amount_due }}</td>
                <td>{{ fee.amount_paid }}</td>
                <td>{{ fee.amount_due|floatformat:2 }} - {{ fee.amount_paid|floatformat:2 }}</td>
                <td>
                    {% if fee.status == "paid" %}
                        <span class="paid">Paid</span>
                    {% elif fee.status == "partial" %}
                        <span class="partial">Partial</span>
                    {% else %}
                        <span class="unpaid">Unpaid</span>
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
    """
    
    # Very complex template with multiple loops and calculations
    very_complex_template = """
    <div class="financial-summary">
        <h2>Financial Summary</h2>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Fees</h3>
                <p class="amount">
                    {% with total=0 %}
                        {% for fee in fees %}
                            {% with total=total|add:fee.amount_due %}{% endwith %}
                        {% endfor %}
                        {{ total|floatformat:2 }}
                    {% endwith %}
                </p>
            </div>
            
            <div class="card">
                <h3>Total Payments</h3>
                <p class="amount">
                    {% with total=0 %}
                        {% for payment in payments %}
                            {% with total=total|add:payment.amount %}{% endwith %}
                        {% endfor %}
                        {{ total|floatformat:2 }}
                    {% endwith %}
                </p>
            </div>
            
            <div class="card">
                <h3>Total Expenses</h3>
                <p class="amount">
                    {% with total=0 %}
                        {% for expense in expenses %}
                            {% with total=total|add:expense.amount %}{% endwith %}
                        {% endfor %}
                        {{ total|floatformat:2 }}
                    {% endwith %}
                </p>
            </div>
        </div>
        
        <div class="payments-by-method">
            <h3>Payments by Method</h3>
            <ul>
                {% regroup payments by method as payment_methods %}
                {% for method in payment_methods %}
                    <li>
                        {{ method.grouper }}:
                        {% with total=0 %}
                            {% for payment in method.list %}
                                {% with total=total|add:payment.amount %}{% endwith %}
                            {% endfor %}
                            {{ total|floatformat:2 }}
                        {% endwith %}
                    </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    """
    
    # Create an engine
    engine = Engine.get_default()
    
    # Compile the templates
    simple_tmpl = engine.from_string(simple_template)
    complex_tmpl = engine.from_string(complex_template)
    very_complex_tmpl = engine.from_string(very_complex_template)
    
    # Render simple template
    context = Context({"students": students})
    start_time = time.time()
    simple_output = simple_tmpl.render(context)
    simple_elapsed = time.time() - start_time
    print(f"Simple template rendered in {simple_elapsed:.4f} seconds")
    
    # Render complex template
    context = Context({"fees": fees})
    start_time = time.time()
    complex_output = complex_tmpl.render(context)
    complex_elapsed = time.time() - start_time
    print(f"Complex template rendered in {complex_elapsed:.4f} seconds")
    
    # Render very complex template
    context = Context({
        "fees": fees,
        "payments": payments,
        "expenses": expenses
    })
    start_time = time.time()
    very_complex_output = very_complex_tmpl.render(context)
    very_complex_elapsed = time.time() - start_time
    print(f"Very complex template rendered in {very_complex_elapsed:.4f} seconds")
    
    
    # Batch rendering test (like a report with many rows)
    start_time = time.time()
    for i in range(100):
        complex_tmpl.render(context)
    batch_elapsed = time.time() - start_time
    print(f"100 complex template renderings in {batch_elapsed:.4f} seconds (avg: {batch_elapsed/100:.4f}s per render)")

if __name__ == "__main__":
    measure_template_performance()

