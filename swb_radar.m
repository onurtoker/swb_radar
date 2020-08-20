pkg load zeromq

% number of test frequencies
num_freq=200;
% number of data points
num_data=4000;
fstart=1.9e9;
fstop=4.2e9;

% lo 
lo_vals=linspace(fstart,fstop,num_freq);
Hvals=zeros(1,num_freq);

for k=1:num_freq
 
  % XMLRPC
  lo_freq = lo_vals(k);
  system(sprintf('python3 py_xlmrpc.py %f', lo_freq));
  pause(0.1);
  
  % ZMQ
  sock1 = zmq_socket(ZMQ_SUB);  % socket-connect-opt-close = 130 us
  zmq_connect(sock1,"tcp://127.0.0.1:5555");
  zmq_setsockopt(sock1, ZMQ_SUBSCRIBE, "");
  recv=zmq_recv(sock1, num_data*8*2, 0); % *2: interleaved channels
  vector=typecast(recv,"single complex"); % char -> float
  
  % DSP
  x0=vector(1:2:length(vector));
  x1=vector(2:2:length(vector));
  X0 = fftshift(fft(x0));
  X1 = fftshift(fft(x1));
  [~,kx0]=max(abs(X0));
  [~,kx1]=max(abs(X1));
  Hvals(k) = X1(kx1)/X0(kx0);

  zmq_close (sock1);

end
 
figure(1); hold on;
hrf=4;
N=num_freq;
BW=(fstop-fstart)*N/(N-1);
wf=cos(pi*[-N/2:N/2-1]/N);
S=fftshift(ifft(wf.*fftshift(Hvals),hrf*N));
S=S/max(abs(S));
plot((linspace(0,N-1,N*hrf)-N/2)*3e8/BW/2, abs(S), '-','linewidth', 2);
grid;
xlabel('Distance (m)');
ylabel('Normalized CIR');
xlim([0 8]);
ylim([0 1.2]);


