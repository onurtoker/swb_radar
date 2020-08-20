
[nfreq, ns] = size(mydata_x0);

Hvals = zeros(1,nfreq);
for k=1:nfreq
  x0 = mydata_x0(k,:);
  x1 = mydata_x1(k,:);
  X0 = fftshift(fft(x0));
  X1 = fftshift(fft(x1));
  [~,kx0]=max(abs(X0));
  [~,kx1]=max(abs(X1));
  Hvals(k) = X1(kx1)/X0(kx0);
end

figure(1); hold on;
plot(fvals/1e9, abs(Hvals), 'linewidth', 2);
ylim([0 1.2*max(abs(Hvals))]);
xlabel('Freq (GHz)');
grid;

figure(2); hold on;
plot(fvals/1e9, 180/pi*unwrap(angle(Hvals)),'linewidth', 2);
xlabel('Freq (GHz)');
grid;

figure(3); hold on;
hrf=4;
N=length(fvals);
BW=(max(fvals)-min(fvals))*N/(N-1);
wf=cos(pi*[-N/2:N/2-1]/N);
S=fftshift(ifft(wf.*(fftshift(Hvals)),hrf*N));
S=S/max(abs(S));
plot((linspace(0,N-1,N*hrf)-N/2)*3e8/BW/2, abs(S), '-','linewidth', 2);
grid;
xlabel('Distance (m)');
xlim([0 8]);
ylim([0 1.2]);
ylabel('Normalized CIR');
grid;



