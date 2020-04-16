var express = require('express');
var router = express.Router();

var trends_controller =require('../Controller/trends_controller');
var search_controller = require('../Controller/search_controller');

/* GET home page. */
router.get('/', function(req, res, next) {
    res.render('index');
});

// GET request for rendering a search engine 
router.get('/search', search_controller.search);

// GET request for rendering the trends page
router.get('/trends', trends_controller.trends);

// // If manager requests to list info about theaters
// router.get('/theaterDetail/getInfo', manager_controller.theater_detail_update);

// // Get and post for manager schedule movie
// router.get('/managerScheduleMoviePlay', manager_controller.schedule_movie_get);

// // Get and post for manager schedule movie
// router.post('/managerScheduleMoviePlay', manager_controller.schedule_movie_post);



module.exports = router;
