let NOOP = () => {};


function prepareAddEditForm(formId) {
    let form = new FormData($(formId)[0]);
    // form.set('authors', )
    let authors = new Set();
    let genres = new Set();

    $('.author-select').each((_, v) => {
        authors.add(parseInt(v.value));
    });

    $('.genre-select').each((_, v) => {
        genres.add(parseInt(v.value));
    });

    form.set('authors', JSON.stringify(Array.from(authors)));
    form.set('genres', JSON.stringify(Array.from(genres)));

    return form;
}


function sendRequest(url, prepareForm, success, error, method) {
    success = success || NOOP;
    error = error || NOOP;
    let data = (prepareForm || NOOP)();
    if (data) {
        $.ajax({
            url: url,
            data: data,
            processData: false,
            contentType: false,
            type: method || 'POST',
            success: success,
            error: error
        });
    }
}