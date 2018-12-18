// Read the contents of the csv file into here
var csvData;

// Keeps track of the indices of any matches - number of elements must be >= columns
let matchArray = new Array(16);

// Number of entries to display when there is no filter applied
const NUM_DEFAULT_ENTRIES = 1000;


// Get the csv file from the server
function getData_ajax() {
    return $.ajax({
        type:    "GET",
        url:     "CMIP5_tabl.csv",
        success: function(text) {
            // `text` is the file text
            console.log("Loading data...");
            // Parse the csv file into an array
            csvData = (Papa.parse(text)).data;
            console.log("Complete!");
        },
        error:   function() {
            console.log("Could not GET table htm file");
        }
        });
}

// Wait for ajax to complete
$.when(getData_ajax()).done(function () {
    // In case the document isn't ready, wait
    $(document).ready(function() {
        $('.filter').multifilter();
        
        // trigger a change event - which will cause the default values to be displayed
        $('.filter').first().change();
    });
});


// jQuery code for filtering
(function($) {
  "use strict";
  $.fn.multifilter = function(options) {
    var settings = $.extend( {
      'target'        : $('table'),
      'method'    : 'thead' // This can be thead or class
    }, options);

    jQuery.expr[":"].Contains = function(a, i, m) {
      return (a.textContent || a.innerText || "").toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
    };
      
      this.each(function() {
          let $this = $(this);
          
          // When the value changes and the user presses enter or clicks off the field - this function will run
          $this.change(function() {
              let filter = $this.val();
              let name = $this.attr('name');
              
              let matchIndex = 0;       // Index of the filter - TBD
              let numMatches = 0;       // Number of matches found
              let matches = [];         // Array of the matches
              let numberFilters = csvData[0].length;
              
              // Figure out which index this filter refers to
              for( let ind = 0; ind < numberFilters; ind++ ) {
                  if( name == csvData[0][ind]) {
                      matchIndex = ind;
                  }
              }
              
              // Only perform a search if there is a filter applied to this entry
              if( filter ) {
                  // Create a regular expression from the filter
                  let filterPattern = new RegExp("^" + filter, 'i');
                  
                  // Search the array for data matching the filter - ignore the header
                  for( let i = 1; i < csvData.length; i++) {
                      
                      if( filterPattern.test(String(csvData[i][matchIndex])) ) {
                          // Found a match - add it to the array
                          numMatches += 1;
                          matches.push(i);
                      }
                  }
              }
              else {
                  // Since there is no filter - delete this array so we don't confuse it with an array with no matches
                  matches = null;
              }
              
              // Add this to the match array
              matchArray[matchIndex] = matches;
              
              // Now go through and figure out which entires are matched in all filters
              // First find the filter with the least number of matches
              // NOTE: Also check if there are no filters applied
              let first = true;
              let minLength = 0;//matchArray[0].length;
              let minIndex = 0;
              let numFilters = 0;
              
              for( let i = 0; i < numberFilters; i++ ) {
                  
                  if( matchArray[i] ) {
                      // Valid array - continue
                      numFilters += 1;
                      
                      let thisLength = matchArray[i].length;
                      
                      if(first == true) {
                          // THis is the first valid array found - thus so far it is the smallest
                          minLength = thisLength;
                          minIndex = i;
                          first = false;
                      }
                      else if( thisLength <= minLength ) {
                          // Found a smaller array
                          minLength = thisLength;
                          minIndex = i;
                      }
                  }
              }
              
              console.log("Num filters: " + numberFilters);
              console.log("Min Length: " + minLength);
              console.log("Min Index: " + minIndex);
              
              // Result array will contain only entries that are in all filters
              let resultArray = [];
              
              // Iterate through the smallest array and see if there are matches in the other filters
              // Only an index that is in all the filters will be accepted
              for( let i = 0; i < minLength; i++ ) {
                  
                  let filterCrossCheck = matchArray[minIndex][i];
                  let foundMatch = true;    // True until proven false
                  
                  // Iterate through all the filters
                  for( let j = 0; j < numberFilters; j++ ) {
                      
                      // Ignore any empty filters or the minIndex array
                      if( matchArray[j] && (j != minIndex) ) {
                          
                          let localMatch = false;
                          
                          // Iterate through all the elements in this filter
                          for ( let k = 0; k < matchArray[j].length; k++ ) {
                              if ( filterCrossCheck == matchArray[j][k] ) {
                                  // Found a match!
                                  localMatch = true;
                                  break;
                              }
                          }
                          
                          // If we found a match, continue to the next filter, otherwise stop
                          if( localMatch == false ) {
                              // No match, stop
                              foundMatch = false;
                              break;
                          }
                      }
                  }
                  
                  // If foundMatch is still true, then add this to the resultArray
                  if( foundMatch == true ) {
                      resultArray.push(filterCrossCheck);
                  }
              }
              
              // Check numFilters - if zero then no filters have been applied - in which case simply add the first X entires into resultArray
              // Start from 1 so we don't add the header
              if( numFilters == 0 ) {
                  for( let i = 1; i < NUM_DEFAULT_ENTRIES + 1; i++) {
                      resultArray.push(i);
                  }
                  
                  console.log("Added " + resultArray.length + " default entires");
              }
              
              // Remove and re-add the tbody element to refresh the table
              $("tbody").remove();
              $("table").append($("<tbody></tbody>"));
              
              // Now finally... add the html elements to the table for viewing...
              for (let i = 0; i < resultArray.length; i++) {
                  let htmlTR = [
                      '<tr>',
                      '  <td>' + csvData[(resultArray[i])][0] + '</td>',    // Variable
                      '  <td>' + csvData[(resultArray[i])][1] + '</td>',    // Model
                      '  <td>' + csvData[(resultArray[i])][2] + '</td>',    // Experiment
                      '  <td>' + csvData[(resultArray[i])][3] + '</td>',    // Frequency
                      '  <td>' + csvData[(resultArray[i])][4] + '</td>',    // Realm
                      '  <td>' + csvData[(resultArray[i])][5] + '</td>',    // Ensemble
                      '  <td>' + csvData[(resultArray[i])][6] + '</td>',    // Status
                      '</tr>'
                      ].join('\n');
                  
                    $("tbody").append($(htmlTR));
              }
              
              return false;
          
          }).keyup(function() {
              //$this.change();
              
      });
    });
  };
})(jQuery);
