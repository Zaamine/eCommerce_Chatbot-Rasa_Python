    <!-- Snippet of the code I used to integrate the chatbot into a PHP e-commerce website -->
    
    <!-- Chatbot integration -->
    <?php
      if(isset($_SESSION["userId"]))
      {
        $user_sessionId = $_SESSION["userId"];
      }
      else
      {
        $user_sessionId = "userIsNotLoggedIn";
      }
      echo '<div id="userSessionIdHiddenDiv" style="display: none;">
          <input type="hidden" name="userSessionIdHiddenField" id="userSessionIdHiddenField" value="'.$user_sessionId.'"/>
          </div>';

      if(!isset($_SESSION["viewsNumber"]) || $_SESSION["viewsNumber"] == 0)
      {
        $_SESSION["viewsNumber"] = 0;
      }
      $_SESSION["viewsNumber"] += 1;
      $viewNumber = $_SESSION["viewsNumber"];
      echo '<div id="viewsNumberHiddenDiv" style="display: none;">
              <input type="hidden" name="viewsNumberHiddenField" id="viewsNumberHiddenField" value="'.$viewNumber.'"/>
            </div>';
    ?>

    <div id="webchat"></div>
    <script src="https://cdn.jsdelivr.net/npm/rasa-webchat/lib/index.min.js"></script>
    <script>
      userSessionIdValue = jQuery("#userSessionIdHiddenField").val()
      viewsNumberValue = jQuery("#viewsNumberHiddenField").val()

      WebChat.default.init({
          selector: "#webchat",
          initPayload: "/greet",
          customData: {"language": "en", "session_userId": userSessionIdValue}, // arbitrary custom data. Stay minimal as this will be added to the socket
          socketUrl: "http://localhost:5005",
          socketPath: "/socket.io/",
          title: "eAssistant, the chatbot",
          subtitle: "Pleased to help you :)",
          params: {"storage": "session"} // can be set to "local"  or "session". details in storage section.
        })

      if((viewsNumberValue == 1) && (userSessionIdValue != "userIsNotLoggedIn") && WebChat.isOpen())
      {
        WebChat.send("/justLoggedInWhileChatting")
      }
      else if((viewsNumberValue == 1) && (userSessionIdValue == "userIsNotLoggedIn") && WebChat.isOpen())
      {
        WebChat.send("/justLoggedOutWhileChatting")
      }
    </script>
    <!-- End of the chatbot integration -->
