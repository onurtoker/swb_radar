
% import XMLRPC library
import org.apache.xmlrpc.client.XmlRpcClient;

% XMLRPC related config
xmlrpc_url = 'http://localhost:8080'
client = javaObject('org.apache.xmlrpc.client.XmlRpcClient')
config = javaObject('org.apache.xmlrpc.client.XmlRpcClientConfigImpl')
url = javaObject('java.net.URL', xmlrpc_url)
config.setServerURL(url)
client.setConfig(config)

f=2.4e9;    
disp(f);

try
    client.execute('set_freq', f)   
catch XE
    % some of these exceptions may be harmless, but always check
    % disp(XE);
    ;
end

    