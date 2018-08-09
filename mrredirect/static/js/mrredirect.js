// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.
var getRedirect = function(redirectData) {
  var bugUrl = redirectData.dataset.bmoUrl + "show_bug.cgi?id=" +
      redirectData.dataset.bugId;
  var reviewId = null;
  var commentId = null;

  if (!window.location.hash.startsWith("#review")) {
    return bugUrl;
  }

  reviewId = parseInt(window.location.hash.slice(7));
  if (reviewId === NaN) {
    return bugUrl;
  }

  commentId = redirectData.dataset["review-" + reviewId];
  if (commentId === undefined) {
    return bugUrl;
  }

  return bugUrl + "#c" + commentId;
};


document.addEventListener("DOMContentLoaded", function() {
  var redirectData = document.getElementById("redirectdata");
  var redirectAnchor = document.getElementById("redirect_anchor");
  var redirect = getRedirect(redirectData);
  redirectAnchor.href = redirect;
  redirectAnchor.textContent = redirect;
  redirectData.setAttribute("class", "show");
  window.location = redirect;
});
