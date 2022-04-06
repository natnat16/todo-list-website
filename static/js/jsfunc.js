function set_field_display() {
  // a function to control display of new category field in new list modal
  var choice = document.getElementById('category').value;
  var fields = document.getElementsByClassName('new_cat');
  //console.log(choice);
  if (choice == 'Add new..') {
    fields[0].style.display = "inline-block";
    fields[1].style.display = "inline-block";
  } else {
    fields[0].style.display = "none";
    fields[1].style.display = "none";
    fields[1].value = "General";
  };
}

function update_db_task(ItemId) {
  // a function for getting the task checkbox status and updating the db
  // ItemId: chk-item.id
  var checkbox_status = document.getElementById(ItemId).checked;

  var status = {
    item_id: ItemId.split('-')[1],
    is_checked: checkbox_status
  };

  // posting data to flask in order to update db without refreshing
  fetch(window.origin + '/update_task_status', {
    method: 'POST',
    credentials: 'include',
    body: JSON.stringify(status),
    cache: 'no-cache',
    headers: new Headers({
      'content-type': 'application/json'
    })
  });

  console.log(window.origin + '/update_task_status');
}

function update_db_task_text(ItemId) {
  // a function for getting the changed task text, unchecking the task
  // and updating the db

  // ItemId: item.id
  var text = document.getElementById('text-' + ItemId).textContent;
  checkbox = document.getElementById('chk-' + ItemId).checked = 0;


  var status = {
    item_id: ItemId,
    text: text,
    unchecked: 0
  };

  console.log(text)

  // posting data to flask in order to update db without refreshing
  fetch(window.origin + '/update_task_text', {
    method: 'POST',
    credentials: 'include',
    body: JSON.stringify(status),
    cache: 'no-cache',
    headers: new Headers({
      'content-type': 'application/json'
    })
  });

  console.log(window.origin + '/update_task_text');

}


function update_db_date(ItemId) {
  // a function for getting the task set due date and updating the db
  // ItemId: date-item.id
  var date = document.getElementById(ItemId).value;

  var status = {
    item_id: ItemId.split('-')[1],
    date: date
  };

  console.log(status);
  // posting data to flask in order to update db without refreshing
  fetch(window.origin + '/update_task_date', {
    method: 'POST',
    credentials: 'include',
    body: JSON.stringify(status),
    cache: 'no-cache',
    headers: new Headers({
      'content-type': 'application/json'
    })
  });

  console.log(window.origin + '/update_task_date');
}


function update_db_color_by_cat(ColorId) {
  // a function for getting the category color picked and updating the db
  // ColorId: opt-category-color
  var radio_status = document.getElementById(ColorId).checked;

  var status = {
    category: ColorId.split('-')[1],
    color: ColorId.split('-')[2],
    radio: radio_status,
    filter_cat: window.location.href.includes('category')
  };

  // console.log(status);
  // posting data to flask in order to update db
  fetch(window.origin + '/update_category_color', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify(status),
      cache: 'no-cache',
      headers: new Headers({
        'content-type': 'application/json'
      })
    })
    // if the fetch succeded following flask redirection home
    .then(function(response) {
      if (response.redirected) {
        window.location.href = response.url;
      }

    })
    // if the fetch failed (rejected)..
    .catch(function(e) {
      console.log('failed')
    })

  console.log(window.origin + '/update_category_color');

}

function update_db_color_by_list(ColorId) {
  // a function for getting the list color picked and updating the db
  // ColorId: opt-color-list.id
  var radio_status = document.getElementById(ColorId).checked;

  var status = {
    list_id: ColorId.split('-')[2],
    color: ColorId.split('-')[1],
    radio: radio_status
  };

  // console.log(status);
  // posting data to flask in order to update db
  fetch(window.origin + '/update_list_color', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify(status),
      cache: 'no-cache',
      headers: new Headers({
        'content-type': 'application/json'
      })
    })
    // if the fetch succeded following flask redirection home
    .then(function(response) {
      if (response.redirected) {
        window.location.href = response.url;
      }

    })
    // if the fetch failed (rejected)..
    .catch(function(e) {
      console.log('failed')
    })

  console.log(window.origin + '/update_list_color');

}


function preparePrint(printout, ListContents) {
  // a function for preparing the print doc
  var header = ListContents.getElementsByClassName("card-header")[0].innerText;
  var tasks = ListContents.getElementsByClassName("task-text");
  var dates = ListContents.getElementsByClassName("date-picker");
  var len = tasks.length;
  //console.log(dates)
  printout.title = "lists";
  printout.document.write('<html>');
  printout.document.write('<head><title>My Lists</title></head>')
  printout.document.write('<body > <h3>' + header + '</h3> <ul>');

  for (let i = 0; i < len; i++) {
    printout.document.write('<li>' + tasks[i].innerText);
    var dueDate = dates[i].getAttribute("value");
    if (dueDate != '') {
      printout.document.write('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{' + dueDate + '}</li>');
    }
  }
  printout.document.write('</ul><hr></body></html>');

  return printout;
}

function printList(ListId) {
  // a function for printing a single list
  // ListId: card-list.id
  var ListContents = document.getElementById(ListId);
  var printout = window.open('', '', 'height=800, width=800');
  printout = preparePrint(printout, ListContents)
  printout.document.close();
  printout.print();
}


function printAll() {
  // a function for printing all lists
  var AllListContents = document.getElementsByClassName("card");
  var printout = window.open('', '', 'height=800, width=800');
  var len = AllListContents.length;
  for (let i = 0; i < len; i++) {
    printout = preparePrint(printout, AllListContents[i]);
  }
  printout.document.close();
  printout.print();
}
