import React, { Component } from 'react';
import $ from 'jquery';
import '../stylesheets/FormView.css';

class FormView extends Component {
  constructor(props) {
    super();
    this.state = {
      question: '',
      answer: '',
      difficulty: 1,
      category: 1,
      categories: {},
      newCategory: '', // State for the new category
    };
  }

  componentDidMount() {
    this.loadCategories();
  }

  loadCategories = () => {
    $.ajax({
      url: `http://127.0.0.1:5000/categories`,
      type: 'GET',
      success: (result) => {
        this.setState({ categories: result.categories });
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again');
        return;
      },
    });
  };

  submitQuestion = (event) => {
    event.preventDefault();
    $.ajax({
      url: 'http://127.0.0.1:5000/questions',
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        question: this.state.question,
        answer: this.state.answer,
        difficulty: this.state.difficulty,
        category: this.state.category,
      }),
      success: (result) => {
        document.getElementById('add-question-form').reset();
        return;
      },
      error: (error) => {
        console.error(error);
        alert('Unable to add question. Please try your request again');
        return;
      },
    });
  };

  submitCategory = (event) => {
    event.preventDefault();
    $.ajax({
      url: 'http://127.0.0.1:5000/categories',
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        category: this.state.newCategory,
      }),
      success: (result) => {
        alert('Category added successfully!');
        this.setState({ newCategory: '' });
        this.loadCategories(); // Reload categories after adding a new one
        return;
      },
      error: (error) => {
        console.error(error);
        alert('Unable to add category. Please try your request again');
        return;
      },
    });
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  render() {
    return (
      <div>
        <div id='add-form'>
          <h2>Add a New Trivia Question</h2>
          <form
            className='form-view'
            id='add-question-form'
            onSubmit={this.submitQuestion}
          >
            <label>
              Question
              <input type='text' name='question' onChange={this.handleChange} />
            </label>
            <label>
              Answer
              <input type='text' name='answer' onChange={this.handleChange} />
            </label>
            <label>
              Difficulty
              <select name='difficulty' onChange={this.handleChange}>
                <option value='1'>1</option>
                <option value='2'>2</option>
                <option value='3'>3</option>
                <option value='4'>4</option>
                <option value='5'>5</option>
              </select>
            </label>
            <label>
              Category
              <select name='category' onChange={this.handleChange}>
                {Object.keys(this.state.categories).map((id) => {
                  return (
                    <option key={id} value={id}>
                      {this.state.categories[id]}
                    </option>
                  );
                })}
              </select>
            </label>
            <input type='submit' className='button' value='Submit' />
          </form>
        </div>

        <div id='add-category-form'>
          <h2>Add a New Category</h2>
          <form onSubmit={this.submitCategory}>
            <label>
              New Category
              <input
                type='text'
                name='newCategory'
                value={this.state.newCategory}
                onChange={this.handleChange}
              />
            </label>
            <input type='submit' className='button' value='Add Category' />
          </form>
        </div>
      </div>
    );
  }
}

export default FormView;
