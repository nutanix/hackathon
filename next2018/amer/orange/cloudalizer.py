from flask import Flask, request, Response


app = Flask(__name__)


action_queue = []


@app.route("/")
def main():
  return "Nutanix Hackathon 2018 - Did It All For The Cookies"


@app.route("/cmd", methods=['GET', 'POST'])
def cmd():
  global action_queue

  if request.method == 'POST':
    request_data = request.get_json()
    print request_data
    action = request_data.get("params")

    if not action:
      raise ValueError("Action is missing - got %r" % action)
    action_queue.append(action)
    return "Request received! Outstanding requests: %d" % len(action_queue)

  elif request.method == 'GET':
    if len(action_queue):
      action = action_queue.pop()
      print "Sending action '%s' to clusterizer" % action
      return Response(action, status=200, mimetype='application/json')
    else:
      return Response("Nothing to do - try again later", status=503)

  else:
    return Response("Method not supported", status=405)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
