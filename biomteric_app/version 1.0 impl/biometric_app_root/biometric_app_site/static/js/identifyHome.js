/**
 * identifyHome.js
 * Author : Achuthanand
 * 
 * This js is used to manage the events of Home page
 */

 /**
  * To trigger the AssignActiveNavBtn method when the document is ready to load
  */
 $('document').ready(function() {
    AssignActiveNavBtn();
 });

 /**
  * AssignActiveNavBtn is used to get the details of current page loaded and to trigger
  * the active selection of nav button
  */
 function AssignActiveNavBtn() {
    // getting the url details of loaded web page
    var pathName = window.location.pathname;
    var pathDetailList = pathName.split('/');
    var currentPage = pathDetailList[pathDetailList.length - 2];
    var pageIndex = 0;
    if('identify_list' == currentPage) {
        pageIndex = 1;
    }
    // assigning acive class to the clicked nav button in the navigation bar
    $("ul li").eq(pageIndex).addClass('active');
 };


