// let async = require('async');

const { body,validationResult, query } = require('express-validator/check');
const { sanitizeBody, sanitizeQuery } = require('express-validator/filter');





exports.search = [
    
    (req, res, next) => {
        res.render('search');
        
    }

];

exports.search_post = [
    (req, res, next) => {
        var search_content = req.body.search_content;
        var limit = req.body.limit;
        
        var url = "http://127.0.0.1:5000/get_author"
    }

];

