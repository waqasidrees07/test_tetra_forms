from sourcetypes import django_html
from django import forms
from main.models import Person, Book, PersonAddress
from tetra import Library, public
from tetra.components import FormComponent, FormFactory

from main.forms import PersonForm, BookForm, AddressForm

default = Library()


@default.register
class PersonFormComponent(FormComponent):
    form_class = FormFactory.factory(Form=PersonForm)

    def load(self, *args, **kwargs) -> None:
        self.persons = Person.objects.all()
        self.message: str = ""

    @public
    def remove(self, id: int) -> None:
        person = Person.objects.get(id=id)
        person.delete()
        self.message = f"Person {person} successfully deleted."

    # language=html
    template = """
    <div class='card'>
       <h3 class='card-title'>Create a new Person:</h3>
          <form enctype="multipart/form-data" method="post">
            <input type="hidden" name="identifier" >
            {% csrf_token %}
                {% for field in form %}
                  {{field.label}}{% if field.field.required %} *{% endif %}:
                  {{field}}
                  {{field.errors}}
                {% endfor %}
             <button type='submit'>Submit</button>    
          </form>
        <p>Alpine.js: first_name: <span x-text='first_name'></span> 
        last_name: <span x-text='last_name'></span></p>
        <p>Django: first_name: {{first_name}} last_name: 
        {{last_name}}</p>
        <h4>Persons:</h4>
        <ul>
        {% for person in persons %}
          <li>
          {{person}}
          {% if person.attachment %}
            <h6>Attachment</h6>
            <a href="{{person.attachment.url}}" target='_blank'>{{person.attachment}}</a>
          {% endif %}
          <button class="btn btn-danger btn-sm" 
                @click='remove({{person.id}})'>X</button>
          </li>
        {% endfor %}
        </ul>
        {{message}}
    </div>
    """

    def form_valid(self, form) -> None:
        instance = form.save(commit=False)
        instance.save()
        self.message = "Person successfully saved."

    def form_invalid(self, form) -> None:
        self.message = "Error saving person."


@default.register
class BookFormComponent(FormComponent):
    form_class = FormFactory.factory(Form=BookForm)

    def load(self, *args, **kwargs) -> None:
        self.books = Book.objects.all()
        self.message: str = ""
        if hasattr(self, 'author') and self.author:
            self.form.fields["delivery_from"].queryset = PersonAddress.objects.filter(
                person=self.author
            )

    def form_valid(self, form) -> None:
        instance = form.save(commit=False)
        instance.save()
        self.message = "Book successfully saved."

    def form_invalid(self, form) -> None:
        self.message = "Error saving book."
        # Reset queryset based on current author if available
        if self.author:
            self.form.fields["delivery_from"].queryset = PersonAddress.objects.filter(
                person=self.author
            )

    @public
    def remove(self, id: int) -> None:
        book = Book.objects.get(id=id)
        book.delete()
        self.message = f"Book {book} successfully deleted."

    @public.watch("author")
    def update_address(self, value, old_value, attr) -> None:
        self.form.fields["delivery_from"].queryset = PersonAddress.objects.filter(
            person=self.author
        )

    # language=html
    template = """
    <div class='card'>
      <h3 class='card-title'>Create a new Book:</h3>
          <form enctype="multipart/form-data" method="post">
            <input type="hidden" name="identifier" >
            {% csrf_token %}
                {% for field in form %}
                  {{field.label}}{% if field.field.required %} *{% endif %}:
                  {{field}}
                  {{field.errors}}
                {% endfor %}
             <button type='submit'>Submit</button>    
          </form>
        <p>Alpine.js: <span x-text='name'></span> 
        ( <span x-text='author'></span>, <span x-text='color'></span>)
        </p>
        <p>Django: {{name}} ({{author}}, {{color}})</p>
        <h4>Books:</h4>
        <ul>
        {% for book in books %}
          <li>
            {{book}}
            <p>delivery from: {{book.delivery_from}}</p>
            <button class="btn btn-danger btn-sm" 
                @click='remove({{book.id}})'>X</button>
          </li>
        {% endfor %}
        </ul>
        {{message}}
    </div>
    """


@default.register
class AddressFormComponent(FormComponent):
    form_class = FormFactory.factory(Form=AddressForm)

    def load(self, *args, **kwargs) -> None:
        self.address_list = PersonAddress.objects.all()
        self.message: str = ""

    def form_valid(self, form) -> None:
        instance = form.save(commit=False)
        instance.save()
        self.message = "Address successfully saved."

    def form_invalid(self, form) -> None:
        self.message = "Error saving address."

    @public
    def remove(self, id: int) -> None:
        address = PersonAddress.objects.get(id=id)
        address.delete()
        self.message = f"Address '{address}' successfully deleted."

    # language=html
    template: django_html = """
        <div class='card'>
       <h3 class='card-title'>Create a new Address for Person:</h3>
          <form enctype="multipart/form-data" method="post">
            <input type="hidden" name="identifier">
            {% csrf_token %}
                {% for field in form %}
                  {{field.label}}{% if field.field.required %} *{% endif %}:
                  {{field}}
                  {{field.errors}}
                {% endfor %}
             <button type='submit'>Submit</button>    
          </form> 
        <h4>Addresses:</h4>
        <ul>
        {% for address in address_list %}
          <li>
            {{address}}
            <button class="btn btn-danger btn-sm" 
                @click='remove({{address.id}})'>X</button>
          </li>
        {% endfor %}
        </ul>
        {{message}}
    </div>
    """
