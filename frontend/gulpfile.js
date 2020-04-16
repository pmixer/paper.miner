var gulp=require('gulp');
var browserSync = require('browser-sync');
var reload = browserSync.reload;
var nodemon = require('gulp-nodemon');

gulp.task("node", function() {
    nodemon({
        script: './bin/www',
        ext: 'js html',
        env: {
            'NODE_ENV': 'development'
        }
    })
});
 
 
gulp.task('server', gulp.series('node', function() {
    var files = [
        'views/**/*.html',
        'views/**/*.ejs',
        'views/**/*.jade',
        'public/**/*.*'
    ];
 
    //gulp.run(["node"]);
    browserSync.init(files, {
        proxy: 'http://localhost:3000',
        browser: 'chrome',
        notify: false,
        port: 4001 
    });
 
    gulp.watch(files).on("change", reload);
}));