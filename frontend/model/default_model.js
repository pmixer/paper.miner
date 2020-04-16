var mysqlModel = require('mysql-model');

var MyAppModel = mysqlModel.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'Team28'
});

// create models based on our MySQL tables
var Admin = MyAppModel.extend({
    tableName : "admin"
});

var Company = MyAppModel.extend({
    tableName : "company"
});

var Creditcard = MyAppModel.extend({
    tableName : "creditcard"
});

var CreditcardUsage = MyAppModel.extend({
    tableName : "creditcardusage"
});

var Customer = MyAppModel.extend({
    tableName : "customer"
});

var Employee = MyAppModel.extend({
    tableName : "employee"
});

var Manager = MyAppModel.extend({
    tableName : "manager"
});

var Movie = MyAppModel.extend({
    tableName : "movie"
});

var MoviePlay = MyAppModel.extend({
    tableName : "movieplay"
});

var Theater = MyAppModel.extend({
    tableName : "theater"
});


