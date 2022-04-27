const {src, dest,watch} = require("gulp");
const pug = require("gulp-pug");
const sass = require('gulp-sass')(require('sass'));

function html(){
    return src("pug/*.pug")
    .pipe(pug({pretty:true}))
    .pipe(dest("./"))
   
}

function css(){
    return src("scss/*.scss")
    .pipe(sass().on("error", sass.logError))
    .pipe(dest("css"))
    
}


exports.html = html;
exports.css = css;
exports.watch = () =>{
    watch("pug/*.pug",html);
    watch("scss/*.scss",css);
}