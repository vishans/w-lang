function getValidID(id){
    id = id.split(' ');
    return id.join('_');
}

function isElementInViewport (el) {

    // Special bonus for those using jQuery
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();
    
    // if (el.id == 'The_begining'){
    // console.log(`win innerHeight=${window.innerHeight}
    //                  innerWidth=${window.innerWidth}
                     
    //             rect top=${rect.top}
    //             rect bottom=${rect.bottom}
    //             /${el.clientHeight}
    //             frm=${el.clientHeight+rect.top}`)
    // }
   
    return(
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.top >=0 ||
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.bottom >=0
        || (rect.top <=0 && rect.top >= (-1*el.clientHeight)) && ((rect.bottom-window.innerHeight) <= el.clientHeight && (rect.bottom-window.innerHeight) >= 0)
    )


    
}








let sections = $('section .text-box-title');
let subList = $('#sub-list');

sections.each(function(){
    let id = this.innerText;
    $(this.parentElement).attr('id', getValidID(id));
    let parentElement = this.parentElement;
    window.addEventListener('scroll', function(){
        window.requestAnimationFrame(function(){
        if(isElementInViewport(parentElement)){
            $('#' + getValidID(id) + '_listed').css('color', 'green')
        }
        else{
            $('#' + getValidID(id) + '_listed').css('color', 'black')

        }
    } )
    })
    let newA = document.createElement('a');
    newA.innerText = id;
    newA.href = '#' + getValidID(id);
    $(newA).attr('id',getValidID(id) + '_listed')
    newA.onclick = function(){
        if($(window).innerWidth() < 769){
            
            $('body').css({'overflow-y' : ' scroll'})
            $('.text-box').css({'color': 'black',
                'text-shadow': 'none'})

            sideBar.removeClass('show');
            sideBar.addClass('hide');
            


            sideBarButton.text('list');

            sideButtonActive = false;
        }
    }
    subList.append(newA);
})



// Dispatch it.
window.dispatchEvent(new Event('scroll'));